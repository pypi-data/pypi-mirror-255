import argparse
import threading

from bec_lib import RedisConnector, ServiceConfig, bec_logger

import data_processing
from data_processing.lmfit1d_service import LmfitService1D

logger = bec_logger.logger
bec_logger.level = bec_logger.LOGLEVEL.INFO


def main():
    """
    Launch the data processing server.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", default="", help="path to the config file")
    clargs = parser.parse_args()
    config_path = clargs.config

    config = ServiceConfig(config_path)

    bec_server = data_processing.dap_server.DAPServer(
        config=config, connector_cls=RedisConnector, provided_services=[LmfitService1D]
    )
    bec_server.start()

    try:
        event = threading.Event()
        logger.success(
            f"Started DAP server for {bec_server._service_id} services. Press Ctrl+C to stop."
        )
        event.wait()
    except KeyboardInterrupt:
        bec_server.shutdown()
        event.set()
