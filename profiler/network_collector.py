
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


def format_error(exc):

    if isinstance(exc, psutil.AccessDenied):
        code = "ACCESS_DENIED"

    elif isinstance(exc, psutil.NoSuchProcess):
        code = "NO_SUCH_PROCESS"

    else:
        code = "UNKNOWN_ERROR"

    return {
        "code": code,
        "message": str(exc)
    }


def collect_connections(kind="inet"):

    result = []
    errors = []

    try:
        connections = psutil.net_connections(kind=kind)

    except (psutil.Error, OSError) as exc:
        return {
            "result": [],
            "errors": [],
            "error": format_error(exc)
        }

    for con in connections:

        connection_info = get_connection_info(con)

        try:
            if con.type == socket.SOCK_STREAM:
                protocol = "TCP"

            elif con.type == socket.SOCK_DGRAM:
                protocol = "UDP"

            else:
                continue

        except (psutil.Error, OSError, AttributeError) as exc:
            errors.append({
                **connection_info,
                "error": format_error(exc)
            })
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
            errors.append({
                **connection_info,
                "error": format_error(exc)
            })

        try:
            if con.raddr:
                remote_ip = con.raddr.ip
                remote_port = con.raddr.port
        except (psutil.Error, OSError, AttributeError, TypeError) as exc:
            errors.append({
                **connection_info,
                "error": format_error(exc)
            })

        try:
            pid = con.pid
        except (psutil.Error, OSError, AttributeError) as exc:
            pid = None
            errors.append({
                **connection_info,
                "error": format_error(exc)
            })

        if protocol == "TCP":
            try:
                status = con.status
            except (psutil.Error, OSError, AttributeError) as exc:
                errors.append({
                    **connection_info,
                    "error": format_error(exc)
                })

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
