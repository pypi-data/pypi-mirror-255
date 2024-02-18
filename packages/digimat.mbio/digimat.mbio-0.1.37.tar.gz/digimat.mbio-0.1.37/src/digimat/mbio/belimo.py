#!/bin/python

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mbio import MBIOGateway

from .device import MBIODevice
# from prettytable import PrettyTable

from .xmlconfig import XMLConfig


class MBIODeviceBelimo(MBIODevice):
    def __init__(self, gateway: MBIOGateway, address, xml: XMLConfig = None):
        super().__init__(gateway, address, xml=xml)
        self._serialNumber=None

    def familySuffix(self):
        if self._serialNumber:
            return (self._serialNumber >> 8) & 0xff

    def familyCode(self):
        if self._serialNumber:
            return self._serialNumber & 0xff

    def deviceCategory(self):
        if self._serialNumber:
            return self.familySuffix() & 0xf

    def builtinModule(self):
        if self._serialNumber:
            return (self.familySuffix() >> 8) & 0xf


class MBIODeviceBelimoP22RTH(MBIODeviceBelimo):
    def onInit(self):
        self._vendor='Belimo'
        self._model='P-22RTH'
        self.setPingInputRegister(0)
        self.readonly=self.valueDigital('readonly', writable=True)
        self.t=self.value('t', unit='C')
        self.hr=self.value('hr', unit='%')
        self.dewp=self.value('dewp', unit='C')
        self.co2=self.value('co2', unit='ppm')

        self.config.set('readonly', False)
        self.config.set('icons', False)
        self.config.set('fan', False)
        self.config.set('setpoint', False)
        self.config.set('temperature', False)
        self.config.set('hygrometry', False)
        self.config.set('iaq', False)
        self.config.set('iaqled', False)
        self.config.set('dark', False)

    def onLoad(self, xml: XMLConfig):
        self.config.dark=xml.match('theme', 'dark')
        self.config.update('readonly', xml.getBool('readonly'))
        self.config.temperature=xml.hasChild('temperature')
        self.config.hygrometry=xml.hasChild('hygrometry')

        item=xml.child('iaq')
        if item:
            self.config.iaq=True
            self.config.iaqled=item.getBool('led', True)
            self.config.set('iaqwarning',  item.getInt('warning', 800))
            self.config.set('iaqalarm', item.getInt('alarm', 1200))
            self.co2alarm=self.valueDigital('co2alarm')

        if xml.child('Icons'):
            self.config.icons=True
            self.cooling=self.valueDigital('cooling', writable=True, default=False)
            self.heating=self.valueDigital('heating', writable=True, default=False)

        item=xml.child('Fan')
        if item:
            self.config.fan=True
            self.config.set('fanboost', item.getBool('boost', False))
            self.config.set('fanstages', item.getInt('stages', 3, vmin=3, vmax=4))
            self.fanAuto=self.valueDigital('fanauto', writable=True)
            self.fanSpeed=self.value('fanspeed', unit='%', writable=True)

        item=xml.child('Setpoint')
        if item:
            self.config.setpoint=True
            self.config.set('spmodeabsolute', not item.getBool('relative', False))
            self.config.set('spzero', item.getFloat('zero', 22.0))
            self.config.set('sprange', item.getFloat('range', 3.0))
            self.spT=self.value('spt', unit='C', writable=True)

    def probe(self):
        self.logger.debug('Probing device address %d' % self.address)
        r=self.readInputRegisters(100, 4)
        if r:
            self._serialNumber=(r[0] << 32) + (r[1] << 16) + r[2]
            data={'version': str(r[3]/100.0),
                  'model': self.familyCode(),
                  'category': self.deviceCategory(),
                  'module': self.builtinModule()}
            return data

    def poweron(self):
        # Comfort Mode
        self.writeRegistersIfChanged(30, 1)

        if self.config.dark:
            self.writeRegistersIfChanged(130, 1)
        else:
            self.writeRegistersIfChanged(130, 0)

        readonly=self.readonly.isOn()
        if self.config.readonly:
            readonly=True
        self.writeRegistersIfChanged(33, not readonly)

        self.writeRegistersIfChanged(132, 1)
        self.writeRegistersIfChanged(141, 0)

        # small values on the left
        if self.config.setpoint:
            self.writeRegistersIfChanged(131, self.config.temperature)
        else:
            # if setpoint not activated, disable small temperature and enable big temperature
            self.writeRegistersIfChanged(131, 0)
        self.writeRegistersIfChanged(132, self.config.hygrometry)
        self.writeRegistersIfChanged(133, self.config.iaq)
        if self.config.iaq:
            if self.config.iaqled:
                self.writeRegistersIfChanged(117, 1)
                self.writeRegistersIfChanged(115, self.config.iaqwarning)
                self.writeRegistersIfChanged(116, self.config.iaqalarm)
            else:
                self.writeRegistersIfChanged(117, 0)
        else:
            self.writeRegistersIfChanged(117, 0)

        if self.config.setpoint:
            self.writeRegistersIfChanged(147, int(self.config.sprange*2.0))

            if self.config.spmodeabsolute:
                self.writeRegistersIfChanged(146, int(self.config.spzero)*100)
                self.writeRegistersIfChanged(145, 0)
            else:
                self.writeRegistersIfChanged(145, 1)

            self.writeRegistersIfChanged(137, 2)
        else:
            if self.config.temperature:
                self.writeRegistersIfChanged(137, 1)
            else:
                self.writeRegistersIfChanged(137, 0)

        # HeatCool Icons
        self.writeRegistersIfChanged(32, 0)
        self.writeRegistersIfChanged(134, self.config.icons)

        # Fan
        self.writeRegistersIfChanged(139, 1)
        if self.config.fan:
            self.writeRegistersIfChanged(138, 1)
            self.writeRegistersIfChanged(148, self.config.fanstages-1)
            self.writeRegistersIfChanged(140, self.config.fanboost)
            self.writeRegistersIfChanged(31, 1)
            self.writeRegistersIfChanged(149, 1)
        else:
            self.writeRegistersIfChanged(138, 0)
            self.writeRegistersIfChanged(148, 2)
            self.writeRegistersIfChanged(140, 0)

        # Warning Icon
        self.writeRegistersIfChanged(135, 2)

        return True

    def poweroff(self):
        self.writeRegistersIfChanged(33, 0)
        return True

    def refresh(self):
        r=self.readInputRegisters(0, 5)
        if r:
            self.t.updateValue(r[0]/100)
            self.hr.updateValue(r[2]/100)
            self.co2.updateValue(r[3])
            self.dewp.updateValue(r[4]/100)

        if self.config.iaq:
            r=self.readHoldingRegisters(6, 1)
            if r:
                self.co2alarm.updateValue(r[0]>=3)

        r=self.readInputRegisters(21, 2)
        if r:
            if self.config.setpoint:
                self.spT.updateValue(r[0]/100)

            if self.config.fan:
                self.fanSpeed.updateValue(r[1]/100)
                r=self.readInputRegisters(31, 1)
                if r:
                    self.fanAuto.updateValue(r[0])

        return 5.0

    def sync(self):
        value=self.readonly
        if value.isPendingSync():
            if self.writeRegisters(33, not value.toReachValue):
                value.clearSyncAndUpdateValue()

        if self.config.setpoint:
            value=self.spT
            if value.isPendingSync():
                if self.writeRegisters(21, int(value.toReachValue*100)):
                    value.clearSync()

        if self.config.fan:
            value=self.fanAuto
            if value.isPendingSync():
                if self.writeRegisters(31, value.toReachValue):
                    value.clearSync()
            value=self.fanSpeed
            if value.isPendingSync():
                if self.writeRegisters(22, int(value.toReachValue*100)):
                    value.clearSync()

        if self.config.icons:
            if self.heating.isPendingSync() or self.cooling.isPendingSync():
                if self.heating.toReachValue:
                    self.writeRegisters(32, 1)
                elif self.cooling.toReachValue:
                    self.writeRegisters(32, 2)
                else:
                    self.writeRegisters(32, 0)

                self.heating.clearSyncAndUpdateValue()
                self.cooling.clearSyncAndUpdateValue()


if __name__ == "__main__":
    pass
