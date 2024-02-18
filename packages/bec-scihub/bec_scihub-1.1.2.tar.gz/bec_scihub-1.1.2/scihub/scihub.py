from bec_lib import BECService, BECStatus, ServiceConfig
from bec_lib.connector import ConnectorBase

from scihub.scibec import SciBecConnector
from scihub.scilog import SciLogConnector


class SciHub(BECService):
    def __init__(self, config: ServiceConfig, connector_cls: ConnectorBase) -> None:
        super().__init__(config, connector_cls, unique_service=True)
        self.config = config
        self.scibec_connector = None
        self.scilog_connector = None
        self._start_scibec_connector()
        self._start_scilog_connector()
        self.status = BECStatus.RUNNING

    def _start_scibec_connector(self):
        self.wait_for_service("DeviceServer")
        self.scibec_connector = SciBecConnector(self, self.connector)

    def _start_scilog_connector(self):
        self.scilog_connector = SciLogConnector(self, self.connector)

    def shutdown(self):
        super().shutdown()
        if self.scibec_connector:
            self.scibec_connector.shutdown()
        if self.scilog_connector:
            self.scilog_connector.shutdown()
