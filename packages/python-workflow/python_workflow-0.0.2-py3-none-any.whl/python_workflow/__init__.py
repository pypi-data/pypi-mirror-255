import logging
import psutil
import math
from datetime import datetime
from time import time

import gevent
from gevent.pool import Pool

logger = logging.getLogger('python-workflow')


class Task:
    def __init__(self, name=None, *args, **kwargs):
        self._name = name
        self._start_at = None
        self._stop_at = None
        self._value = None
        self._args = args
        self._kwargs = kwargs

    def is_completed(self):
        return self._stop_at is not None

    def run(self):
        """ Must be implemented """

    def on_start(self):
        message = '%s is starting ...' % (self.__class__.__name__)

        """ Must be implemented """
        logger.debug(' [%s][%s] %s args=%s, kwargs=%s' % (
            datetime.now().isoformat(),
            str(self.name).ljust(30),
            message.ljust(50),
            self._args,
            self._kwargs
        ))

    def on_complete(self):
        message = '%s completed (%ss.)' % (
            self.__class__.__name__,
            math.ceil(self.duration * 10000) / 10000
        )

        """ Must be implemented """
        logger.debug(' [%s][%s] %s args=%s, kwargs=%s' % (
            datetime.now().isoformat(),
            str(self.name).rjust(30),
            message.ljust(50),
            self._args,
            self._kwargs
        ))

    def on_error(self, *args, **kwargs):
        raise args[0]

    def reset(self):
        self._start_at = None
        self._stop_at = None

    def start(self):
        if self._start_at is None:
            self._start_at = time()

        self.on_start()

        try:
            self._value = self.run()
        except Exception as e:
            self.on_error(e)

        self.stop()
        self.on_complete()
        return self._value

    def stop(self):
        if self._stop_at is None:
            self._stop_at = time()
        return self._stop_at

    @property
    def duration(self):
        if self._stop_at is not None and self._start_at is not None:
            return self._stop_at - self._start_at

    @property
    def name(self):
        return self._name

    @property
    def stop_at(self):
        return self._stop_at

    @property
    def start_at(self):
        return self._start_at

    @property
    def value(self):
        return self._value


class Step(Task):
    gevent.hub.Hub.NOT_ERROR = (Exception,)

    def __init__(self, name=None, tasks=None, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        if not isinstance(tasks, list):
            raise Exception('`tasks` must be a instance of List')

        for task in tasks:
            if not isinstance(task, Task):
                raise Exception('`task` must be a instance of Task')
        self.tasks = tasks

    def run(self):
        value = {}

        size = psutil.cpu_count() / 2
        pool = Pool(size=size)
        jobs = [pool.spawn(task.start) for task in self.tasks]
        pool.join(raise_error=True)

        for idx, task in enumerate(self.tasks):
            value[
                '%s-%s' % (task.name, idx)
            ] = jobs[idx].value
        return value

    def reset(self):
        super().reset()
        for task in self.tasks:
            task.reset()


class Workflow(Task):
    def __init__(self, name=None, steps=None, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        if not isinstance(steps, list):
            raise Exception('`steps` must be a instance of List')

        for step in steps:
            if not isinstance(step, Step):
                raise Exception('`step` must be a instance of Step')
        self.steps = steps

    def run(self):
        value = {}
        for idx, step in enumerate(self.steps):
            value[
                '%s-%s' % (step.name, idx)
            ] = step.start()
        return value

    def reset(self):
        super().reset()
        for step in self.steps:
            step.reset()
