from enum import Enum


class Error(Enum):
    NotFound = "File not found"
    PermissionError = "Permission Error opening file"
    SocketError = "Error opening socket"
    TimeoutError = "Timed out error"
    ConfigParseError = "Error parsing configuration file"
    ProcessError = "Error occurrec process system process"
    NoSuchProcess = "No Such Process"
    AccessDenied = "Access Denied"
    ZombieProcess = "Zombie Process"

