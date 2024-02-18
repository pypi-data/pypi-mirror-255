"""Background work."""

from threading import Thread
from multiprocessing import Process
from multiprocessing.util import _exit_function
import atexit
from flask import current_app


class MetricsThread(object):
    """[summary]

    Args:
        object ([type]): [description]
    """

    def __init__(self, app=None, target=None, args=(), kwargs={}) -> None:

        if app is not None and target is not None:
            self._init_thread(app, target, args, kwargs)

    def _init_thread(self, app, target, args, kwargs):
        with app.app_context():
            app.logger.info(f"Starting thread {target.__name__}")
            self.thrd = _FlaskThread(target=target, args=args, kwargs=kwargs)

            self.thrd.start()


class _FlaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = current_app._get_current_object()

    def run(self):
        """[summary]"""
        with self.app.app_context():
            super().run()


class MetricsProcess(object):
    """[summary]

    Args:
        object ([type]): [description]
    """

    def __init__(self, app=None, target=None, args=(), kwargs={}):
        atexit.unregister(_exit_function)
        if app is not None and target is not None:

            self._start_process(app, target, args, kwargs)

    def _start_process(self, app, target, args, kwargs):
        app.logger.info(f"Starting process {target.__name__}")

        self.prs = _FlaskProcess(target=target, conf=app.config, args=args, kwargs=kwargs)

        self.prs.start()


class _FlaskProcess(Process):
    def __init__(self, conf=None, *args, **kwargs):
        self.conf = None
        if conf:
            self.conf = conf
        super().__init__(*args, **kwargs)

    def run(self):
        from py_flaskbase.application import create

        print(type(self.conf))
        _app = create()
        _app.config = self.conf
        with _app.app_context():
            super().run()
