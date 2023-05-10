import sys
# from play_youtube import VirtualHuman
# from custom_thread import CustomThread
from sock import SSHSock5Proxy
from util import load_sock_servers, run_socks
import asyncio
from error import Error
import toml
from result import Result, Ok, Err
from typing import Any, List

if __name__ == "__main__":
    # load configuration file
    config: dict[str, Any] = toml.load("settings/config.toml")

    TIMEOUT_IN_SECS: int = config['timeout']
    NUMBER_OF_PARALLEL: int = config['number_of_parallel']

    print("STARTING IROBOT!!!")
    print("Loading sock server file")
    loaded_sock_servers: Result[List[SSHSock5Proxy], Error] = load_sock_servers("settings/servers.txt")

    match loaded_sock_servers:
        case Ok(value):
            sock_servers = value
        case Err(err):
            print("Error loading or parsing proxy file")
            sys.exit(2)

    loop = asyncio.get_event_loop()
    for i in range(0, len(sock_servers), 5):
        loop.run_until_complete(run_socks(sock_servers[i:i+NUMBER_OF_PARALLEL]))
        print(f"Completed {i+NUMBER_OF_PARALLEL} proxies")

    print("Exiting")
