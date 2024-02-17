#!/bin/python

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mbio import MBIO

# import time
import time
import threading

from prettytable import PrettyTable

from .items import Items
from .value import MBIOValues
from .config import MBIOConfig
from .xmlconfig import XMLConfig

from .value import MBIOValue, MBIOValueWritable
from .value import MBIOValueDigital, MBIOValueDigitalWritable
from .value import MBIOValueMultistate, MBIOValueMultistateWritable


class MBIOTask(object):
    STATE_HALT = 0
    STATE_POWERON = 1
    STATE_RUN = 2
    STATE_POWEROFF = 3
    STATE_ERROR = 4

    def __init__(self, parent: MBIO, name, xml: XMLConfig = None):
        self._parent=parent
        if not name:
            name='task%d' % parent.tasks.count()
        self._name=str(name).lower()
        self._key='%s' % self._name
        self._state=self.STATE_HALT
        self._error=False
        self._timeoutState=0
        self._values=MBIOValues(self, self._key, self.logger)
        self._eventReset=threading.Event()
        self._eventStop=threading.Event()
        self._eventHalt=threading.Event()
        self._parent.declareTask(self)
        # FIXME: daemon=True ?
        self._thread=threading.Thread(target=self.manager)
        self.logger.info("Starting TASK:%s" % self._key)

        self._config=MBIOConfig()

        self.onInit()
        self.load(xml)

        self._thread.start()

    @property
    def parent(self) -> MBIO:
        return self._parent

    def getMBIO(self) -> MBIO:
        return self._parent

    @property
    def config(self) -> MBIOConfig:
        return self._config

    @property
    def logger(self):
        return self._parent.logger

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def values(self):
        return self._values

    def value(self, name, unit=None, default=None, writable=False, resolution=0.1):
        key=self.values.computeValueKeyFromName(name)
        value=self.values.item(key)
        if not value:
            if writable:
                value=MBIOValueWritable(self.values, name, unit=unit, default=default, resolution=resolution)
            else:
                value=MBIOValue(self.values, name, unit=unit, default=default)
        return value

    def valueDigital(self, name, default=None, writable=False):
        key=self.values.computeValueKeyFromName(name)
        value=self.values.item(key)
        if not value:
            if writable:
                value=MBIOValueDigitalWritable(self.values, name, default=default)
            else:
                value=MBIOValueDigital(self.values, name, default=default)
        return value

    def valueMultistate(self, name, vmax, vmin=0, default=None, writable=False):
        key=self.values.computeValueKeyFromName(name)
        value=self.values.item(key)
        if not value:
            if writable:
                value=MBIOValueMultistateWritable(self.values, name, vmax, vmin, default=default)
            else:
                value=MBIOValueMultistate(self.values, name, vmax, vmin, default=default)
        return value

    def onInit(self):
        pass

    def onLoad(self, xml: XMLConfig):
        pass

    def load(self, xml: XMLConfig):
        if xml:
            try:
                self.onLoad(xml)
            except:
                self.logger.exception('Task %s:load()' % self.name)

    def isHalted(self):
        if self.state==self.STATE_HALT:
            return True
        return False

    def isError(self):
        if self._error:
            return True
        return False

    def stop(self):
        self._eventStop.set()

    def halt(self):
        self._eventHalt.set()

    def reset(self):
        self._eventHalt.clear()
        self._eventReset.set()

    def waitForThreadTermination(self):
        self.stop()
        self._thread.join()

    def sleep(self, delay=1):
        try:
            if self._eventStop.is_set():
                return True
            return self._eventStop.wait(delay)
        except:
            pass

    def poweron(self) -> bool:
        # to be overriden
        return True

    def poweroff(self) -> bool:
        # to be overriden
        return True

    def run(self) -> float:
        # to be overriden
        return 5.0

    @property
    def state(self):
        return self._state

    def statestr(self):
        states=['HALT', 'POWERON', 'RUN', 'POWEROFF', 'ERROR']
        try:
            return states[self.state]
        except:
            pass
        return 'UNKNOWN:%d' % self._state

    def timeout(self, delay):
        return time.time()+delay

    def isTimeout(self, t):
        if time.time()>=t:
            return True
        return False

    def timeToTimeout(self, timeout):
        return max(0, timeout-time.time())

    def manager(self):
        while not self._eventStop.is_set():
            try:
                self._state=self.STATE_HALT
                if self._eventHalt.is_set():
                    self.sleep(0.5)
                    continue
                self._eventReset.clear()
                self.logger.info("TASK:%s poweron()" % self._key)
                self._state=self.STATE_POWERON
                if self.poweron():
                    self._state=self.STATE_RUN
                    timeout=0.1
                    while True:
                        if timeout is None:
                            timeout=5.0
                        self.sleep(timeout)
                        # self.logger.warning('%s:run()' % self.key)
                        timeout=self.run()

                        if self._eventStop.is_set() or self._eventHalt.is_set():
                            self.logger.info("TASK:%s poweroff()" % self._key)
                            self._state=self.STATE_POWEROFF
                            self.poweroff()
                            break
                        elif self._eventReset.is_set():
                            break
                        self._error=False
                else:
                    self._state=self.STATE_ERROR
            except:
                self.logger.exception("TASK:%s manager()" % self._key)
                self._state=self.STATE_ERROR

            if self._state==self.STATE_ERROR:
                self._error=True
                timeout=self.timeout(15)
                while not self._eventStop.is_set():
                    if self._eventReset.is_set() or self.isTimeout(timeout):
                        break
                    if self._eventHalt.is_set():
                        break
                    self.sleep(0.5)

        self.logger.info("TASK:%s done" % self._key)

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.key, self.statestr())

    def registerValue(self, value):
        self.parent.registerValue(value)


class MBIOTasks(Items):
    def __init__(self, logger):
        super().__init__(logger)
        self._items: list[MBIOTask]=[]
        self._itemByKey={}
        self._itemByName={}

    def item(self, key):
        item=super().item(key)
        if item:
            return item

        item=self.getByKey(key)
        if item:
            return item

        item=self.getByName(key)
        if item:
            return item

    def add(self, item: MBIOTask) -> MBIOTask:
        if isinstance(item, MBIOTask):
            super().add(item)
            self._itemByName[item.name]=item
            self._itemByKey[item.key]=item

    def getByName(self, name):
        try:
            return self._itemByName[name]
        except:
            pass

    def getByKey(self, key):
        try:
            return self._itemByKey[key]
        except:
            pass

    def stop(self):
        for item in self._items:
            item.stop()

    def reset(self):
        for item in self._items:
            item.reset()

    def halt(self):
        for item in self._items:
            item.halt()

    def resetHalted(self):
        for item in self._items:
            if item.isHalted():
                item.reset()

    def waitForThreadTermination(self):
        for item in self._items:
            item.waitForThreadTermination()


if __name__=='__main__':
    pass
