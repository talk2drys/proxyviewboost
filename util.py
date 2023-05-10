import sys
import os

from play_youtube import VirtualHuman
from sock import SSHSock5Proxy
from typing import List
from result import Result, Ok, Err
import asyncio
import psutil
from error import Error


def load_sock_servers(path: str) -> Result[List[SSHSock5Proxy], Error]:
    current_line: int = 0
    proxies: List[SSHSock5Proxy] = []

    try:
        with open(os.path.join(sys.path[0], path), "r") as file_handle:
            print("parsing sock file loaded")
            for line in file_handle:
                splitted_line = line.split(' ')
                if len(splitted_line) != 4:
                    print(f"Error parsing sock server on line {current_line}")
                    Err(Error.ConfigParseError)
                sock5_server = SSHSock5Proxy(host=splitted_line[0], port=int(splitted_line[1]),
                                             username=splitted_line[2], password=splitted_line[3].rstrip())
                proxies.append(sock5_server)
                current_line = current_line + 1
        return Ok(proxies)
    except FileNotFoundError:
        return Err(Error.NotFound)
    except PermissionError:
        return Err(Error.PermissionError)


def kill_process_on_port(port: int) -> Result[None, Error]:
    # Get a list of all processes listening on the given port
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} ({proc.name()})")
                    proc.kill()
                    return Ok(None)
        except psutil.ZombieProcess:
            return Err(Error.ZombieProcess)
        except psutil.NoSuchProcess:
            return Err(Error.NoSuchProcess)
        except psutil.AccessDenied:
            return Err(Error.AccessDenied)
    return Ok(None)


async def run_sock(proxy: SSHSock5Proxy):
    client = proxy
    match await client.create_ssh_sock():
        case Ok(_):
            pass
        case Err(_):
            pass

    human = VirtualHuman(youtube_url="https://www.youtube.com/watch?v=agy_bokLzO4")
    socks5_url = client.__str__()
    await human.run(socks5_url)

    bind_port = client.get_binding_port()
    if bind_port is None:
        print(proxy.get_host_and_port())
        return

    print("killing ssh process")
    if kill_process_on_port(bind_port).is_err():
        print(f"error killing socket with port {client.get_binding_port}")


async def run_socks(proxies):
    tasks = []
    for proxy in proxies:
        task = asyncio.create_task(run_sock(proxy))
        tasks.append(task)
    await asyncio.gather(*tasks)
