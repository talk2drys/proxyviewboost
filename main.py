import sys
from sock import SSHSock5Proxy
from util import load_sock_servers, run_socks
import asyncio
from error import Error
import toml
from result import Result, Ok, Err
from typing import Any, List
from logger import  set_logger
from app_config import NUMBER_OF_PARALLEL

if __name__ == "__main__":
    logger = set_logger()

    logger.info("STARTING IROBOT!!!")
    logger.info("Loading sock server file")
    logger.debug("Loading sock server file")
    loaded_sock_servers: Result[List[SSHSock5Proxy], Error] = load_sock_servers("settings/servers.txt")

    match loaded_sock_servers:
        case Ok(value):
            sock_servers = value
        case Err(err):
            logger.error("Error loading or parsing proxy file")
            sys.exit(2)

    loop = asyncio.get_event_loop()
    for i in range(0, len(sock_servers), NUMBER_OF_PARALLEL):
        loop.run_until_complete(run_socks(sock_servers[i:i + NUMBER_OF_PARALLEL]))
        logger.info(f"Completed {i + NUMBER_OF_PARALLEL} proxies")

    logger.info("Exiting")
