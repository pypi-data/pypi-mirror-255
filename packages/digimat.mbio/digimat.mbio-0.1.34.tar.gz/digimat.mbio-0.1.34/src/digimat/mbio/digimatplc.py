#!/bin/python

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mbio import MBIOGateway

from .device import MBIODevice
from prettytable import PrettyTable

from .xmlconfig import XMLConfig


class MBIODeviceDigimatPLC(MBIODevice):
    NBCHANNELDI=4
    NBCHANNELDO=4
    NBCHANNELAI=4
    NBCHANNELAO=4

    def onInit(self):
        self._vendor='Digimat'
        self._model='PLC'

        self.setPingInputRegister(98)

        self.config.set('watchdog', 60)
        self.config.set('boards', 1)

        self.DI=[]
        self.DO=[]
        self.AI=[]
        self.AO=[]
        self.LEDR=[]
        self.LEDG=[]
        self.LEDB=[]

    def AO_raw2state(self, value, raw):
        if raw is not None:
            state=raw/10000*100.0
            lrange=value.config.lrange
            hrange=value.config.hrange
            if lrange>0 or hrange<100:
                state=max(lrange, state)
                state=min(hrange, state)
                state=(state-lrange)/(hrange-lrange)*100
            return state

    def AO_state2raw(self, value, state):
        if state is not None:
            lrange=value.config.lrange
            hrange=value.config.hrange
            state=min(state, value.config.max)
            state=max(state, value.config.min)
            if lrange>0 or hrange<100:
                raw=10000/100.0*(lrange+(hrange-lrange)*state/100.0)
            else:
                raw=state/100.0*10000
            return int(raw)

    def onLoad(self, xml: XMLConfig):
        self.config.update('watchdog', xml.getInt('watchdog'))
        self.config.update('boards', xml.getInt('boards', vmin=1, vmax=7))

        for board in range(self.config.boards):
            self.LEDR.append(self.valueDigital('ledr%d' % board, writable=True))
            self.LEDG.append(self.valueDigital('ledg%d' % board, writable=True))
            self.LEDB.append(self.valueDigital('ledb%d' % board, writable=True))

        for channel in range(self.NBCHANNELDI*self.config.boards):
            value=self.valueDigital('di%d' % channel)
            value.config.set('invert', False)
            self.DI.append(value)

            item=xml.child(value.name)
            if item:
                if not item.getBool('enable', True):
                    value.disable()
                value.config.xmlUpdateBool(item, 'invert')

        for channel in range(self.NBCHANNELDO*self.config.boards):
            value=self.valueDigital('do%d' % channel, writable=True)
            value.config.set('invert', False)
            value.config.set('default', None)
            self.DO.append(value)

            item=xml.child(value.name)
            if item:
                if not item.getBool('enable', True):
                    value.disable()
                value.config.xmlUpdateBool(item, 'invert')
                value.config.xmlUpdateBool(item, 'default')

        for channel in range(self.NBCHANNELAI*self.config.boards):
            value=self.value('ai%d' % channel)
            value.config.set('type', 'pt1000')
            value.config.set('resolution', 0.1)
            value.config.set('offset', 0)
            self.AI.append(value)

            item=xml.child(value.name)
            if item:
                if not item.getBool('enable', True):
                    value.disable()
                value.config.xmlUpdate(item, 'type')
                value.config.xmlUpdateFloat(item, 'resolution', vmin=0)
                value.config.xmlUpdateFloat(item, 'offset')
                if value.config.contains('type', '10v'):
                    value.config.set('unit', 'V')
                    value.config.xmlUpdate(item, 'unit')
                    value.config.set('x0', 0.0)
                    value.config.xmlUpdateFloat(item, 'x0')
                    value.config.set('x1', 10.0)
                    value.config.xmlUpdateFloat(item, 'x1', vmin=value.config.x0)
                if value.config.contains('type', '20ma'):
                    value.config.set('unit', '%')
                    value.config.xmlUpdate(item, 'unit')
                    value.config.set('x0', 0.0)
                    value.config.xmlUpdateFloat(item, 'x0')
                    value.config.set('x1', 100.0)
                    value.config.xmlUpdateFloat(item, 'x1', vmin=value.config.x0)

            value.resolution=value.config.resolution

        for channel in range(self.NBCHANNELAO*self.config.boards):
            value=self.value('ao%d' % channel, unit='%', writable=True)
            value.setRange(0, 100)
            value.config.set('default', None)
            value.config.set('lrange', 0)
            value.config.set('hrange', 100)
            value.config.set('resolution', 1)
            value.config.set('min', 0)
            value.config.set('max', 100)
            value.config.set('ramp', 0)
            self.AO.append(value)

            item=xml.child(value.name)
            if item:
                if not item.getBool('enable', True):
                    value.disable()
                value.config.xmlUpdateFloat(item, 'default')
                value.config.xmlUpdateFloat(item, 'lrange', vmin=0, vmax=100)
                value.config.xmlUpdateFloat(item, 'hrange', vmin=value.config.lrange, vmax=100)
                value.config.xmlUpdateFloat(item, 'resolution', vmin=0)
                value.config.xmlUpdateInt(item, 'min', vmin=0, vmax=100)
                value.config.xmlUpdateInt(item, 'max', vmin=value.config.min, vmax=100)
                value.config.xmlUpdateInt(item, 'ramp', vmin=0)
            value.resolution=value.config.resolution

    def getBoardConfigRegister0(self, board):
        return 35+(4*board)

    def poweronDI(self):
        pass

    def poweronDO(self):
        for board in range(self.config.boards):
            configRegister0=self.getBoardConfigRegister0(board)
            channel0=board*self.NBCHANNELDO
            data=0x0
            for channel in range(self.NBCHANNELDO):
                value=self.DO[channel0+channel]
                if value.config.default is not None:
                    state=value.config.default
                    if value.config.invert:
                        state=not state
                    if state:
                        data |= (0x01 << 2*channel)
                    else:
                        data |= (0x00 << 2*channel)
                else:
                    data |= (0x10 << 2*channel)
            self.writeRegistersIfChanged(configRegister0, data)

    def poweronAI(self):
        for board in range(self.config.boards):
            configRegister0=self.getBoardConfigRegister0(board)
            channel0=board*self.NBCHANNELAI
            data=0x0
            for channel in range(self.NBCHANNELAI):
                value=self.AI[channel0+channel]
                if value.config.type is not None:
                    if value.config.type=='pt1000':
                        data |= (0x7 << 4*channel)
                        value.unit='C'
                    elif value.config.type=='pt100':
                        data |= (0x3 << 4*channel)
                        value.unit='C'
                    elif value.config.type=='ntc':
                        data |= (0x0 << 4*channel)
                        value.unit='C'
                    elif '20ma' in value.config.type:
                        data |= (0x01 << 4*channel)
                        value.unit='%'
                        if value.config.get('unit'):
                            value.unit=value.config.unit
                    elif '10v' in value.config.type:
                        data |= (0x02 << 4*channel)
                        value.unit='V'
                        # allow custom unit
                        if value.config.get('unit'):
                            value.unit=value.config.unit
                else:
                    # PT1000
                    data |= (0x7 << 4*channel)
                    value.unit='C'

            self.writeRegistersIfChanged(configRegister0+0, data)

    def poweronAO(self):
        for board in range(self.config.boards):
            configRegister0=self.getBoardConfigRegister0(board)
            channel0=board*self.NBCHANNELAO
            data=0x0
            for channel in range(self.NBCHANNELAO):
                value=self.AO[channel0+channel]
                if value.config.default is not None:
                    data |= (0x1 << channel)
                    self.writeRegistersIfChanged(configRegister0+1,
                        self.AO_state2raw(value, value.config.default))

            self.writeRegistersIfChanged(configRegister0+2, data)

    def poweron(self):
        # FIXME:
        r=self.readHoldingRegisters(68, 2)
        self.logger.warning(r)

        self.poweronDI()
        self.poweronDO()
        self.poweronAI()
        self.poweronAO()
        return True

    def poweronsave(self):
        self.writeRegisters(70, 0xAAAA)

    def poweroff(self):
        return True

    def refreshDI(self):
        r=self.readDiscreteInputs(0, 8*self.config.boards)
        if r:
            for board in range(self.config.boards):
                channel0=board*self.NBCHANNELDI
                for channel in range(self.NBCHANNELDI):
                    value=self.DI[channel0+channel]
                    value.updateValue(r[board*8+channel])

    def refreshDO(self):
        r=self.readCoils(0, 8*self.config.boards)
        if r:
            for board in range(self.config.boards):
                channel0=board*self.NBCHANNELDO
                for channel in range(self.NBCHANNELDO):
                    value=self.DO[channel0+channel]
                    value.updateValue(r[board*8+channel])

                self.LEDR[board].updateValue(r[board*8+7])
                self.LEDG[board].updateValue(r[board*8+5])
                self.LEDB[board].updateValue(r[board*8+6])

    def refreshAI(self):
        r=self.readInputRegisters(0, self.config.boards*4)
        if r:
            for board in range(self.config.boards):
                channel0=board*self.NBCHANNELAI
                r0=4*board
                for channel in range(self.NBCHANNELAI):
                    value=self.AI[channel0+channel]
                    data=r[r0+channel]/100.0
                    try:
                        dx=(value.config.x1-value.config.x0)
                        data=value.config.x0+data/10.0*dx
                    except:
                        pass

                    value.updateValue(data+value.config.offset)

    def refreshAO(self):
        r=self.readHoldingRegisters(0, self.config.boards*4)
        if r:
            for board in range(self.config.boards):
                channel0=board*self.NBCHANNELAO
                r0=4*board
                for channel in range(self.NBCHANNELAO):
                    value=self.AO[channel0+channel]
                    state=self.AO_raw2state(value, r[r0+channel])
                    value.updateValue(state)

    def refresh(self):
        self.refreshDI()
        self.microsleep()
        self.refreshDO()
        self.microsleep()
        self.refreshAI()
        self.microsleep()
        self.refreshAO()
        return 2.0

    def sync(self):
        for board in range(self.config.boards):
            self.microsleep()
            channel0=board*self.NBCHANNELDO
            for channel in range(self.NBCHANNELDO):
                value=self.DO[channel0+channel]
                if not value.isEnabled():
                    continue
                if value.isPendingSync():
                    self.signalRefresh(0.1)
                    self.writeCoils(board*8+channel, value.toReachValue)
                    value.clearSync()

            value=self.LEDR[board]
            if value.isPendingSync():
                self.writeCoils(board*8+7, value.toReachValue)
                value.clearSync()
            value=self.LEDG[board]
            if value.isPendingSync():
                self.writeCoils(board*8+5, value.toReachValue)
                value.clearSync()
            value=self.LEDB[board]
            if value.isPendingSync():
                self.writeCoils(board*8+6, value.toReachValue)
                value.clearSync()

        for board in range(self.config.boards):
            self.microsleep()
            channel0=board*self.NBCHANNELAO
            for channel in range(self.NBCHANNELAO):
                value=self.AO[channel0+channel]
                if not value.isEnabled():
                    continue
                if value.isPendingSync():
                    self.signalRefresh(1.0)
                    raw=self.AO_state2raw(value, value.toReachValue)
                    if self.writeRegisters(channel0+channel, raw):
                        value.clearSync()

    def off(self):
        for channel in range(self.NBCHANNELDO):
            self.DO[channel].off()
        for channel in range(self.NBCHANNELAO):
            self.AO[channel].off()

    def on(self):
        for channel in range(self.NBCHANNELDO):
            self.DO[channel].on()
        for channel in range(self.NBCHANNELAO):
            self.AO[channel].on()

    def toggle(self):
        for channel in range(self.NBCHANNELDO):
            self.DO[channel].toggle()
        for channel in range(self.NBCHANNELAO):
            self.AO[channel].toggle()

    def probe(self):
        self.logger.debug('Probing device address %d' % self.address)
        r=self.readInputRegisters(98, 1)
        if r and (r[0] & 0xFF00) == 0xA500:
            data={'version': str(r[0] & 0xff),
                  'model': 'PLC'}
            self.logger.warning(data)
            return data
        return None


if __name__ == "__main__":
    pass
