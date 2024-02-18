from __future__ import annotations

import os
import time
import traceback
import uuid
from typing import TYPE_CHECKING

import bec_lib
from bec_lib import DeviceConfigError
from bec_lib import DeviceManagerBase as DeviceManager
from bec_lib import MessageEndpoints, bec_logger, messages
from bec_lib.connector import ConnectorBase
from bec_lib.scibec_validator import SciBecValidator

if TYPE_CHECKING:
    from bec_lib.device import DeviceBase
    from scihub.scibec.scibec_connector import SciBecConnector

logger = bec_logger.logger

dir_path = os.path.abspath(os.path.join(os.path.dirname(bec_lib.__file__), "./configs/"))


class ConfigHandler:
    def __init__(self, scibec_connector: SciBecConnector, connector: ConnectorBase) -> None:
        self.scibec_connector = scibec_connector
        self.device_manager = DeviceManager(self.scibec_connector.scihub)
        self.device_manager.initialize(scibec_connector.config.redis)
        self.producer = connector.producer()
        self.validator = SciBecValidator(os.path.join(dir_path, "openapi_schema.json"))

    def parse_config_request(self, msg: messages.DeviceConfigMessage) -> None:
        """Processes a config request. If successful, it emits a config reply

        Args:
            msg (BMessage.DeviceConfigMessage): Config request

        """
        try:
            self.device_manager.check_request_validity(msg)
            if msg.content["action"] == "update":
                self._update_config(msg)
            if msg.content["action"] == "reload":
                self._reload_config(msg)
            if msg.content["action"] == "set":
                self._set_config(msg)

        except Exception:
            content = traceback.format_exc()
            self.send_config_request_reply(accepted=False, error_msg=content, metadata=msg.metadata)

    def send_config(self, msg: messages.DeviceConfigMessage) -> None:
        """broadcast a new config"""
        self.producer.send(MessageEndpoints.device_config_update(), msg)

    def send_config_request_reply(self, accepted, error_msg, metadata):
        """send a config request reply"""
        msg = messages.RequestResponseMessage(
            accepted=accepted, message=error_msg, metadata=metadata
        )
        RID = metadata.get("RID")
        self.producer.set(MessageEndpoints.device_config_request_response(RID), msg, expire=60)

    def _set_config(self, msg: messages.DeviceConfigMessage):
        config = msg.content["config"]
        scibec = self.scibec_connector.scibec
        logger.debug(self.scibec_connector.scibec_info)
        experiment = self.scibec_connector.scibec_info.get("beamline", {}).get("activeExperiment")

        # if scibec and experiment:
        #     scibec.set_session_data(experiment, config)
        #     self.scibec_connector.update_session()
        # else:
        for name, device in config.items():
            self._convert_to_db_config(name, device)
            self.validator.validate_device(device)
        self.scibec_connector.set_redis_config(list(config.values()))
        self.send_config_request_reply(accepted=True, error_msg=None, metadata=msg.metadata)
        reload_msg = messages.DeviceConfigMessage(action="reload", config={}, metadata=msg.metadata)
        self.send_config(reload_msg)

    def _convert_to_db_config(self, name: str, config: dict) -> None:
        if "deviceConfig" in config and config["deviceConfig"] is None:
            config["deviceConfig"] = {}
        config["name"] = name

    def _reload_config(self, msg: messages.DeviceConfigMessage):
        # if we have a connection to SciBec, pull the data before forwarding the reload request
        if self.scibec_connector.scibec:
            self.scibec_connector.update_session()
        self.send_config_request_reply(accepted=True, error_msg=None, metadata=msg.metadata)
        self.send_config(msg)
        # self.device_manager.update_status(BECStatus.BUSY)
        # self.device_manager.devices.flush()
        # self.device_manager._get_config()
        # self.device_manager.update_status(BECStatus.RUNNING)

    def _update_config(self, msg: messages.DeviceConfigMessage):
        updated = False
        dev_configs = msg.content["config"]

        for dev, config in dev_configs.items():
            device = self.device_manager.devices[dev]
            updated = self._update_device_config(device, config.copy())
            if updated:
                if "id" in device._config and self.scibec_connector.scibec:
                    self.scibec_connector.scibec.patch_device_config(device._config["id"], config)
                self.update_config_in_redis(device)

        # send updates to services
        if updated:
            self.send_config(msg)
            self.send_config_request_reply(accepted=True, error_msg=None, metadata=msg.metadata)

    def _update_device_server(self, RID: str, config: dict) -> None:
        msg = messages.DeviceConfigMessage(action="update", config=config, metadata={"RID": RID})
        self.producer.send(MessageEndpoints.device_server_config_request(), msg)

    def _wait_for_device_server_update(self, RID: str, timeout_time=10) -> bool:
        timeout = timeout_time
        time_step = 0.05
        elapsed_time = 0
        while True:
            msg = self.producer.get(MessageEndpoints.device_config_request_response(RID))
            if msg:
                return msg.content["accepted"]

            if elapsed_time > timeout:
                raise TimeoutError(
                    "Reached timeout whilst waiting for a device server config reply."
                )

            time.sleep(time_step)
            elapsed_time += time_step

    def _update_device_config(self, device: DeviceBase, dev_config) -> bool:
        updated = False
        if "deviceConfig" in dev_config:
            RID = str(uuid.uuid4())
            self._update_device_server(RID, {device.name: dev_config})
            updated = self._wait_for_device_server_update(RID)
            device._config["deviceConfig"].update(dev_config["deviceConfig"])
            dev_config.pop("deviceConfig")

        if "enabled" in dev_config:
            self._validate_update({"enabled": dev_config["enabled"]})
            device._config["enabled"] = dev_config["enabled"]
            RID = str(uuid.uuid4())
            self._update_device_server(RID, {device.name: dev_config})
            updated = self._wait_for_device_server_update(RID)
            dev_config.pop("enabled")

        if not dev_config:
            return updated

        available_keys = [
            "readOnly",
            "userParameter",
            "onFailure",
            "deviceTags",
            "readoutPriority",
            "softwareTrigger",
        ]
        for key in dev_config:
            if key not in available_keys:
                raise DeviceConfigError(f"Unknown update key {key}.")

            self._validate_update({key: dev_config[key]})
            device._config[key] = dev_config[key]
            updated = True

        return updated

    def _validate_update(self, update):
        self.validator.validate_device_patch(update)

    def update_config_in_redis(self, device):
        config = self.device_manager.producer.get(MessageEndpoints.device_config())
        config = config.content["resource"]
        index = next(
            index for index, dev_conf in enumerate(config) if dev_conf["name"] == device.name
        )
        config[index] = device._config
        msg = messages.AvailableResourceMessage(resource=config)
        self.device_manager.producer.set(MessageEndpoints.device_config(), msg)
