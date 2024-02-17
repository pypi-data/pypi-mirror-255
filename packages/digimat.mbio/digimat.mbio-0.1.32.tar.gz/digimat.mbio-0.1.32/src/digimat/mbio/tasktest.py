#!/bin/python

from .task import MBIOTask
from .xmlconfig import XMLConfig
from .scheduler import Schedulers

import requests


class MBIOTaskPulsar(MBIOTask):
    def onInit(self):
        self._timeout=0
        self._period=1
        self._outputs=[]

    def onLoad(self, xml: XMLConfig):
        mbio=self.getMBIO()
        self._period=xml.getFloat('period', 1)
        items=xml.children('output')
        if items:
            for item in items:
                value=mbio[item.get('key')]
                if value and value.isWritable():
                    self._outputs.append(value)

    def poweron(self):
        self._timeout=self.timeout(self._period)
        return True

    def poweroff(self):
        return True

    def run(self):
        if self._outputs:
            if self.isTimeout(self._timeout):
                self._timeout=self.timeout(self._period)
                for value in self._outputs:
                    value.toggle()
            return min(5.0, self.timeToTimeout(self._timeout))


class MBIOTaskCopier(MBIOTask):
    def onInit(self):
        self._outputs=[]

    def onLoad(self, xml: XMLConfig):
        mbio=self.getMBIO()
        self._source=mbio.value(xml.get('source'))
        items=xml.children('output')
        if items:
            for item in items:
                value=mbio[item.get('key')]
                if value and value.isWritable():
                    self._outputs.append(value)

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def run(self):
        if self._source and self._outputs:
            for value in self._outputs:
                value.set(self._source.value)
            return 1


class MBIOTaskScheduler(MBIOTask):
    def onInit(self):
        self._schedulers=Schedulers()
        self._programs={}
        self._timeoutreload=0
        self._periodReload=0

    def onLoadProgram(self, scheduler, xml: XMLConfig):
        if scheduler is not None and xml is not None:
            items=xml.children('*')
            if items:
                for item in items:
                    if item.tag=='on':
                        scheduler.on(item.get('dow'), item.get('time'), item.getFloat('sp'))
                    elif item.tag=='off':
                        scheduler.off(item.get('dow'), item.get('time'))
                    elif item.tag=='slot':
                        scheduler.on(item.get('dow'), item.get('start'), item.get('stop'), item.getFloat('sp'))

    def onLoad(self, xml: XMLConfig):
        items=xml.children('program')
        if items:
            for item in items:
                name=item.get('name')
                if name and not self._schedulers.get(name):
                    sp=item.child('sp')
                    default=None
                    if sp:
                        default=sp.getFloat('default')
                        unit=sp.get('unit', 'C')
                        resolution=item.getFloat('resolution', 0.1)

                    scheduler=self._schedulers.create(name=name, sp=default)
                    program={'state': self.valueDigital('%s_state' % name)}
                    if sp:
                        program['sp']=self.value('%s_sp' % name, unit=unit, resolution=resolution)
                    self._programs[name]=program
                    self.onLoadProgram(scheduler, item.child('triggers'))

        item=xml.child('download')
        if item and item.child('url'):
            try:
                self.comerr=self.valueDigital('comerr', default=False)
                self._timeoutReload=0
                self._periodReload=item.getInt('period', 3600)
                self._urlReload=item.child('url').text()
                self.logger.error(self._urlReload)
                self.reload()
            except:
                pass

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def reload(self):
        self._timeoutReload=self.timeout(60)
        if self._periodReload>0 and self._urlReload:
            try:
                r=requests.get(self._urlReload, timeout=5.0)
                if r and r.ok:
                    data=r.text

                    # TODO: load
                    self.logger.warning(data)

                    self.comerr.value=False
                    self._timeoutReload=self.timeout(self._periodReload)
                    return True
            except:
                pass

        self.comerr.value=True
        return False

    def run(self):
        if self._periodReload>0 and self.isTimeout(self._timeoutReload):
            self.reload()

        for scheduler in self._schedulers:
            state, sp = scheduler.eval()
            try:
                self._programs[scheduler.name]['state'].updateValue(state)
                self._programs[scheduler.name]['sp'].updateValue(sp)
            except:
                pass
        return 1.0


class MBIOTaskVirtualIO(MBIOTask):
    def onInit(self):
        pass

    def onLoad(self, xml: XMLConfig):
        items=xml.children('digital')
        if items:
            for item in items:
                name=item.get('name')
                if name:
                    self.valueDigital(name, default=item.getBool('default'), writable=True)

        items=xml.children('analog')
        if items:
            for item in items:
                name=item.get('name')
                unit=item.get('unit')
                resolution=item.getFloat('resolution', 0.1)
                if name:
                    self.value(name, unit=unit, default=item.getBool('default'), writable=True, resolution=resolution)

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def run(self):
        for value in self.values:
            # value.updateValue(value.value)
            if value.isPendingSync():
                value.clearSyncAndUpdateValue()
        return 1.0


if __name__ == "__main__":
    pass
