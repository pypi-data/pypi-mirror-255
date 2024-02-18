from bec_lib import BECClient, ServiceConfig, bec_logger
from bec_lib.connector import ConnectorBase

from .dap_service_manager import DAPServiceManager

logger = bec_logger.logger


class DAPServer(BECClient):
    """Data processing server class."""

    def __init__(
        self, config: ServiceConfig, connector_cls: ConnectorBase, provided_services: list
    ) -> None:
        super().__init__()
        self.config = config
        self.connector_cls = connector_cls
        self._dap_service_manager = None
        self._provided_services = (
            provided_services if isinstance(provided_services, list) else [provided_services]
        )

    @property
    def _service_id(self):
        return f"{'_'.join([service.__name__ for service in self._provided_services])}"

    def start(self):
        if not self._provided_services:
            raise ValueError("No services provided")
        self.initialize(self.config, self.connector_cls, wait_for_server=True)
        super().start()
        self._start_dap_serivce()
        bec_logger.level = bec_logger.LOGLEVEL.INFO

    def _start_dap_serivce(self):
        self._dap_service_manager = DAPServiceManager(self._provided_services)
        self._dap_service_manager.start(self)

    def shutdown(self):
        self._dap_service_manager.shutdown()
        super().shutdown()
