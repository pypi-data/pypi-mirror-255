"""Server callbacks."""

from prometheus_client import multiprocess


def on_starting(server) -> None:
    """[summary]

    Args:
        server ([type]): [description]
    """
    print(f"server='{server}'")


def child_exit(server, worker) -> None:
    """[summary]

    Args:
        server ([type]): [description]
        worker ([type]): [description]
    """
    print(f"server='{server}'")

    multiprocess.mark_process_dead(worker.pid)


def worker_exit(server, worker) -> None:
    """[summary]

    Args:
        server ([type]): [description]
        worker ([type]): [description]
    """
    print(f"server='{server}'")

    multiprocess.mark_process_dead(worker.pid)


def when_ready(server, worker) -> None:
    """[summary]

    Args:
        server ([type]): [description]
        worker ([type]): [description]
    """
    print(f"worker='{worker}' server='{server}'")
