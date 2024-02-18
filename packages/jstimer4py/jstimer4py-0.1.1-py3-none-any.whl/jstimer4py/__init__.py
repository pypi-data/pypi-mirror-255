# All rights reserved. Cyan Changes (c) 2024
# Licensed to zhuhansan666 & lovemilk-Inc(lovemilk-Inc@proton.me) under Apache-2.0 license.

import asyncio
import atexit
import datetime
import gc
import inspect
import threading
import warnings

from contextvars import copy_context, Context
from functools import partial, wraps
from threading import Thread
from asyncio import run, Future, Task, Queue, CancelledError as AsyncIOCancelledError
from concurrent.futures import CancelledError as FutureCancelledError
from dataclasses import dataclass, field
from typing import Callable, ParamSpec, TypeVar, Coroutine, Awaitable, cast, Any, Sequence, Optional, Iterable
from itertools import count

__all__ = [
    'set_timeout',
    'set_interval',
    'clear_timeout',
    'clear_interval',
    'SchedulerThread',
    'WorkerThread',
    'shutdown'
]

MAX_TASK_NUM = 0
WORKERS_NUM = 2

P = ParamSpec("P")
R = TypeVar("R")


def run_sync(call: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    """一个用于包装 sync function 为 async function 的装饰器

    参数:
        call: 被装饰的同步函数
    """

    @wraps(call)
    async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_running_loop()
        pfunc = partial(call, *args, **kwargs)
        context = copy_context()
        result = await loop.run_in_executor(None, partial(context.run, pfunc))
        return result

    return _wrapper


def is_coroutine_callable(call: Callable[..., Any]) -> bool:
    """检查 call 是否是一个 callable 协程函数"""
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    func_ = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(func_)


def _transform_handler(func: Callable[[], Awaitable]):
    if is_coroutine_callable(func):
        return cast(Callable[..., Awaitable], func)
    else:
        return run_sync(cast(Callable[..., Any], func))


@dataclass
class ScheduledTask:
    func: Callable
    call_at: datetime.datetime | Iterable[datetime.datetime]
    _interval: bool = None
    id: int = None
    context: Optional[Context] = None
    args: Sequence = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)

    @property
    def is_interval(self):
        return bool(self._interval)


@dataclass(frozen=True)
class Timer:
    __id: int
    __task: ScheduledTask = field(repr=False)

    def __hash__(self):
        return hash(self.__id)


def _id_of(timer: Timer) -> int:
    return getattr(timer, f'__{type(Timer).__name__}_id')


class SchedulerThread(Thread):
    def __init__(self, workers_cnt=WORKERS_NUM):
        super().__init__(daemon=True)
        self.fut = Future()
        self._tasks: dict[int, Task] = {}
        self._counter = count(0)
        self.workers: list[WorkerThread] = [WorkerThread(self) for _ in range(workers_cnt)]
        self.cancelled_ids: Queue[int] = Queue()
        self.pending_tasks: Queue["ScheduledTask"] = Queue(maxsize=MAX_TASK_NUM)
        self.waiting_tasks: Queue["ScheduledTask"] = Queue(maxsize=MAX_TASK_NUM)
        self._loop = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def start(self):
        super().start()

        for worker in self.workers:
            worker.start()

    def add_task(self, task: ScheduledTask):
        task.id = next(self._counter)
        task = self._task(task.id, self.waiting_tasks.put(task))
        asyncio.run_coroutine_threadsafe(self._wait_task(task), self._get_loop()).result()

    async def _schedule_task(self, at: datetime.datetime, task: ScheduledTask):
        assert task.id is not None
        if isinstance(task.call_at, datetime.datetime):
            await asyncio.sleep((at - datetime.datetime.now()).total_seconds())
            await self.pending_tasks.put(task)
        for at in task.call_at:
            await asyncio.sleep((at - datetime.datetime.now()).total_seconds())
            await self.pending_tasks.put(task)

    def _task(self, i: int, coro: Coroutine, loop: asyncio.AbstractEventLoop = None):
        loop = self._get_loop() if loop is None else loop
        assert loop is not None, 'loop must be set'
        _t = loop.create_task(coro, name=f'ScheduledTask-{i}')
        self._tasks[i] = _t
        return _t

    async def _wait_task(self, task: Task):
        return await task

    async def canceller(self):
        while not self.fut.done():
            _id = await self.cancelled_ids.get()
            task = self._tasks.get(_id, None)
            if task is not None:
                task.cancel()

    async def main(self):
        loop = asyncio.get_running_loop()
        self._loop = loop
        try:
            while not self.fut.done():
                task = await self.waiting_tasks.get()
                _ = self._task(task.id, self._schedule_task(task.call_at, task), loop)
        except asyncio.CancelledError:
            return

    def _stop_workers(self):
        for worker in self.workers:
            worker.stop_event.set()

    def stop(self):
        loop = self._get_loop()

        if self.fut.done():
            warnings.warn("Scheduler already stopped")
            return

        if not self.fut.done():
            self.fut.set_result(None)

        if not loop:
            return

        self._stop_workers()

        loop.set_debug(True)

        def shutdown_exception_handler(loop: asyncio.AbstractEventLoop, context: Any):
            if "exception" not in context or not isinstance(
                    context["exception"], asyncio.CancelledError
            ):
                loop.default_exception_handler(context)

        loop.set_exception_handler(shutdown_exception_handler)

        asyncio.run_coroutine_threadsafe(self._cancel(), loop).result()
        loop.stop()

    async def _cancel(self):
        loop = asyncio.get_running_loop()

        for task in self._tasks.values():
            task.cancel()

        ct = asyncio.current_task()

        try:
            await self._cancel_tasks(asyncio.all_tasks(loop=loop), ct)
        except asyncio.CancelledError:
            pass

    async def _cancel_tasks(self, tasks: set[Task], _sk: Task = None):
        try:
            ptasks = set()
            for task in tasks:
                if task is _sk:
                    continue
                task.cancel()
                ptasks.add(task)
            await asyncio.gather(*ptasks)
        except asyncio.CancelledError:
            pass

    def run(self):
        try:
            run(self.main())
        except (AsyncIOCancelledError, RuntimeError):
            self._stop_workers()
            return


def call_task(task: ScheduledTask):
    if task.context is not None:
        task.context.run(task.func, *task.args, **task.kwargs)
    else:
        task.func(*task.args, **task.kwargs)


class WorkerThread(Thread):
    def __init__(self, scheduler: SchedulerThread, stop_event: asyncio.Event = None):
        super().__init__(daemon=True)
        self.scheduler = scheduler
        if stop_event is None:
            stop_event = asyncio.Event()
        self.stop_event = stop_event
        self._stop_task: Optional[Task] = None
        self._main_task: Optional[Task] = None

    async def _stopper(self):
        loop = asyncio.get_running_loop()

        await self.stop_event.wait()

        self._main_task.cancel()

    async def main(self):
        loop = asyncio.get_running_loop()

        self._stop_task = asyncio.create_task(self._stopper())

        while not self.scheduler.fut.done():
            try:
                fut = asyncio.wrap_future(
                    asyncio.run_coroutine_threadsafe(self.scheduler.pending_tasks.get(), self.scheduler._get_loop())
                )
                task = await fut

                await loop.run_in_executor(
                    None, partial(call_task, task)
                )
            except (AsyncIOCancelledError, FutureCancelledError):
                break

    async def wait_and_main(self):
        while self.scheduler._get_loop() is None:
            await asyncio.sleep(0.01)

        if self.scheduler.fut.done():
            return

        self._main_task = asyncio.create_task(self.main())
        await self._main_task

    def run(self):
        run(self.wait_and_main())


_scheduler = SchedulerThread()
_scheduler.start()


def set_timeout(func: Callable, timeout: float, __scheduler: SchedulerThread = _scheduler, *args, **kwargs) -> Timer:
    sc = __scheduler
    task = ScheduledTask(
        func=func,
        args=args, kwargs=kwargs,
        call_at=datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    )
    sc.add_task(task)
    return Timer(task.id, task)


def clear_timeout(timer: Timer, __scheduler: SchedulerThread = _scheduler) -> None:
    sc = __scheduler
    _id = _id_of(timer)
    sc.cancelled_ids.put_nowait(_id)


def set_interval(func: Callable, timeout: float, __scheduler: SchedulerThread = _scheduler, *args, **kwargs) -> Timer:
    sc = __scheduler

    def call_timers(now: datetime.datetime) -> Iterable[datetime.datetime]:
        now += datetime.timedelta(seconds=timeout)
        while True:
            now += datetime.timedelta(seconds=timeout)
            yield now

    task = ScheduledTask(
        func=func,
        args=args, kwargs=kwargs,
        call_at=call_timers(datetime.datetime.now()),
        _interval=True
    )
    sc.add_task(task)
    return Timer(task.id, task)


def shutdown(__scheduler: SchedulerThread = _scheduler) -> None:
    sc = __scheduler
    sc.stop()
    sc.join()


atexit.register(partial(shutdown))

clear_interval = clear_timeout
