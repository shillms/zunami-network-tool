
import socket

import psutil


def get_connection_info(con):

    try:
        pid = con.pid
    except (psutil.Error, OSError, AttributeError):
        pid = None

    try:
        if con.laddr:
            laddr = f"{con.laddr.ip}:{con.laddr.port}"
        else:
            laddr = None
    except (psutil.Error, OSError, AttributeError, TypeError):
        laddr = None

    return {
        "pid": pid,
        "laddr": laddr
    }


def format_error(exc, scope, stage):

    if isinstance(exc, psutil.AccessDenied):
        code = "ACCESS_DENIED"

    elif isinstance(exc, psutil.ZombieProcess):
        code = "ZOMBIE_PROCESS"

    elif isinstance(exc, psutil.NoSuchProcess):
        code = "NO_SUCH_PROCESS"

    elif isinstance(exc, OSError):
        code = "OS_ERROR"

    elif isinstance(exc, AttributeError):
        code = "ATTRIBUTE_ERROR"

    elif isinstance(exc, TypeError):
        code = "TYPE_ERROR"

    else:
        code = "UNKNOWN_ERROR"

    return {
        "scope": scope,
        "stage": stage,
        "code": code,
        "message": str(exc)
    }


def add_connection_error(errors, con, exc, stage):

    errors.append({
        **get_connection_info(con),
        "error": format_error(exc, "connection", stage)
    })


def collect_connections(kind="inet"):

    result = []
    errors = []

    try:
        connections = psutil.net_connections(kind=kind)
    except (psutil.Error, OSError) as exc:
        return {
            "result": [],
            "errors": [],
            "error": format_error(
                exc,
                "global",
                "collect_connections"
            )
        }

    for con in connections:

        try:
            if con.type == socket.SOCK_STREAM:
                protocol = "TCP"

            elif con.type == socket.SOCK_DGRAM:
                protocol = "UDP"

            else:
                continue
        except (psutil.Error, OSError, AttributeError) as exc:
            add_connection_error(
                errors, con, exc, "protocol"
            )
            continue

        local_ip = None
        local_port = None
        remote_ip = None
        remote_port = None
        status = None

        try:
            if con.laddr:
                local_ip = con.laddr.ip
                local_port = con.laddr.port
        except (psutil.Error, OSError, AttributeError, TypeError) as exc:
            add_connection_error(
                errors, con, exc, "local_address"
            )

        try:
            if con.raddr:
                remote_ip = con.raddr.ip
                remote_port = con.raddr.port
        except (psutil.Error, OSError, AttributeError, TypeError) as exc:
            add_connection_error(
                errors, con, exc, "remote_address"
            )

        try:
            pid = con.pid
        except (psutil.Error, OSError, AttributeError) as exc:
            pid = None
            add_connection_error(
                errors, con, exc, "pid"
            )

        try:
            status = con.status
        except (psutil.Error, OSError, AttributeError) as exc:
            add_connection_error(
                errors, con, exc, "status"
            )

        result.append({
            "protocol": protocol,
            "local_ip": local_ip,
            "local_port": local_port,
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "status": status,
            "pid": pid
        })

    return {
        "result": result,
        "errors": errors,
        "error": None
    }
