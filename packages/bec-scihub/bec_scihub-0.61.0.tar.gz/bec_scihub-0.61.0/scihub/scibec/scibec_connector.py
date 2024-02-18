from __future__ import annotations

import os
from typing import TYPE_CHECKING

import msgpack
from bec_lib import MessageEndpoints, bec_logger, messages
from bec_lib.connector import ConnectorBase
from dotenv import dotenv_values
from py_scibec import SciBecCore
from py_scibec.exceptions import ApiException

from scihub.repeated_timer import RepeatedTimer

from .config_handler import ConfigHandler
from .scibec_metadata_handler import SciBecMetadataHandler

if TYPE_CHECKING:
    from scihub import SciHub

logger = bec_logger.logger


class SciBecConnectorError(Exception):
    pass


class SciBecConnector:
    token_expiration_time = 86400  # one day

    def __init__(self, scihub: SciHub, connector: ConnectorBase) -> None:
        self.scihub = scihub
        self.connector = connector
        self.producer = connector.producer()
        self.scibec = None
        self.host = None
        self.target_bl = None
        self.ingestor = None
        self.ingestor_secret = None
        self.ro_user = None
        self.ro_user_secret = None
        self._env_configured = False
        self.scibec_info = {}
        self._config_request_handler = None
        self._metadata_handler = None
        self.config_handler = None
        self._scibec_account_thread = None
        self._start(connector)

    def _start(self, connector: ConnectorBase):
        self.connect_to_scibec()
        self.config_handler = ConfigHandler(self, connector)
        self._start_config_request_handler()
        self._start_metadata_handler()
        self._start_scibec_account_update()

    @property
    def config(self):
        """get the current service config"""
        return self.scihub.config

    def _load_environment(self):
        env_base = self.scihub.config.service_config.get("scibec", {}).get("env_file", "")
        env_file = os.path.join(env_base, ".env")
        if not os.path.exists(env_file):
            # check if there is an env file in the parent directory
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            env_file = os.path.join(current_dir, ".env")
            if not os.path.exists(env_file):
                return

        config = dotenv_values(env_file)
        self._update_config(**config)

    def _update_config(
        # pylint: disable=invalid-name
        self,
        SCIBEC_HOST: str = None,
        SCIBEC_TARGET: str = None,
        SCIBEC_INGESTOR: str = None,
        SCIBEC_INGESTOR_SECRET: str = None,
        SCIBEC_RO_USER: str = None,
        SCIBEC_RO_USER_SECRET: str = None,
        **kwargs,
    ) -> None:
        self.host = SCIBEC_HOST
        self.target_bl = SCIBEC_TARGET
        self.ingestor = SCIBEC_INGESTOR
        self.ingestor_secret = SCIBEC_INGESTOR_SECRET
        self.ro_user = SCIBEC_RO_USER
        self.ro_user_secret = SCIBEC_RO_USER_SECRET

        if (
            self.host
            and self.target_bl
            and self.ingestor
            and self.ingestor_secret
            and self.ro_user
            and self.ro_user_secret
        ):
            self._env_configured = True

    def _start_scibec_account_update(self) -> None:
        """
        Start a repeated timer to update the scibec account in redis
        """
        if not self._env_configured:
            return
        if not self.scibec:
            return
        try:
            self._scibec_account_update()
            self.scibec.login(username=self.ingestor, password=self.ingestor_secret)
        except ApiException as exc:
            logger.warning(f"Could not connect to SciBec: {exc}")
            return
        logger.info("Starting SciBec account update timer.")
        self._scibec_account_thread = RepeatedTimer(
            self.token_expiration_time, self._scibec_account_update
        )

    def _scibec_account_update(self):
        """
        Update the scibec account in redis
        """
        logger.info("Updating SciBec account.")
        token = self.scibec.get_new_token(username=self.ro_user, password=self.ro_user_secret)
        if token:
            self.set_scibec_account(token)

    def set_scibec_account(self, token: str) -> None:
        """
        Set the scibec account in redis
        """
        self.producer.set(
            MessageEndpoints.scibec(),
            messages.CredentialsMessage(
                credentials={"url": self.host, "token": f"Bearer {token}"}
            ).dumps(),
        )

    def set_redis_config(self, config):
        self.producer.set(MessageEndpoints.device_config(), msgpack.dumps(config))

    def _start_metadata_handler(self) -> None:
        self._metadata_handler = SciBecMetadataHandler(self)

    def _start_config_request_handler(self) -> None:
        self._config_request_handler = self.connector.consumer(
            MessageEndpoints.device_config_request(),
            cb=self._device_config_request_callback,
            parent=self,
        )
        self._config_request_handler.start()

    @staticmethod
    def _device_config_request_callback(msg, *, parent, **_kwargs) -> None:
        msg = messages.DeviceConfigMessage.loads(msg.value)
        logger.info(f"Received request: {msg}")
        parent.config_handler.parse_config_request(msg)

    def connect_to_scibec(self):
        """
        Connect to SciBec and set the producer to the write account
        """
        self._load_environment()
        if not self._env_configured:
            logger.warning("No environment file found. Cannot connect to SciBec.")
            return
        try:
            self._update_scibec_instance()
            self._update_experiment_info()
            self._update_eaccount_in_redis()

        except (ApiException, SciBecConnectorError) as exc:
            self.scibec = None
            logger.warning(f"Could not connect to SciBec: {exc}")

    def _update_scibec_instance(self):
        logger.info(f"Connecting to SciBec on {self.host}")
        self.scibec = SciBecCore(host=self.host)
        self.scibec.login(username=self.ingestor, password=self.ingestor_secret)

    def _update_experiment_info(self):
        beamline_info = self.scibec.beamline.beamline_controller_find(
            query_params={"filter": {"where": {"name": self.target_bl}}}
        )
        if not beamline_info.body:
            raise SciBecConnectorError(f"Could not find a beamline with the name {self.target_bl}")
        beamline_info = beamline_info.body[0]
        self.scibec_info["beamline"] = beamline_info
        experiment_id = beamline_info.get("activeExperiment")

        if not experiment_id:
            raise SciBecConnectorError(f"Could not find an active experiment on {self.target_bl}")

        experiment = self.scibec.experiment.experiment_controller_find_by_id(
            path_params={"id": experiment_id}
        )

        if not experiment:
            raise SciBecConnectorError(f"Could not find an experiment with the id {experiment_id}")
        experiment = experiment.body
        self.scibec_info["activeExperiment"] = experiment

    def _update_eaccount_in_redis(self):
        write_account = self.scibec_info["activeExperiment"]["writeAccount"]
        if write_account[0] == "p":
            write_account = write_account.replace("p", "e")
        self.producer.set(MessageEndpoints.account(), write_account.encode())

    def shutdown(self):
        """
        Shutdown the SciBec connector
        """
        if self._scibec_account_thread:
            self._scibec_account_thread.stop()
        if self._config_request_handler:
            self._config_request_handler.shutdown()
        if self._metadata_handler:
            self._metadata_handler.shutdown()
