import subprocess
import asyncio
import socket
from error import Error
from result import Result, Ok, Err
import socket
import asyncssh
from asyncssh import SSHListener, SSHClientConnection


def _get_free_port() -> Result[int, Error]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            return Ok(s.getsockname()[1])
    except socket.error:
        return Err(Error.SocketError)


class SSHSock5Proxy:
    def __init__(self, host: str, port: int, username: str, password: str):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        match _get_free_port():
            case Ok(value):
                self._binding_port = value
            case Error(_):
                self._binding_port = None

    def __str__(self) -> str:
        schema = "socks5"
        return f"{schema}://localhost:{self._binding_port}"

    def get_host_and_port(self) -> str:
        return f"{self._host}:{self._binding_port}"

    def get_binding_port(self) -> int | None:
        return self._binding_port

    def get_host(self) -> str:
        return self._host

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    async def create_ssh_sock(self) -> Result[SSHListener, Error]:
        if self._binding_port is None:
            return Err(Error.SocketError)
        try:
            # TODO: add host key policy
            conn: SSHClientConnection = await asyncssh.connect(self._host, port=self._port, username=self._username,
                                                               password=self._password, known_hosts=None)
            try:
                sock_listener: SSHListener = await conn.forward_socks(listen_host="127.0.0.1", listen_port=0)
                return Ok(sock_listener)
            except OSError:
                return Err(Error.OtherError)
        except Exception as e:
            print(f"Error: {str(e)}")
            Err(Error.OtherError)
