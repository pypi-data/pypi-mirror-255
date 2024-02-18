#!/bin/python

from __future__ import annotations


from .device import MBIODevice
from .xmlconfig import XMLConfig

# from prettytable import PrettyTable


class MBIODeviceMetzConnect(MBIODevice):
    pass


class MBIODeviceMetzConnectMRDO4(MBIODeviceMetzConnect):
    NBCHANNEL=4

    def onInit(self):
        self.config.set('watchdog', 60)
        self.OVR=self.valueDigital('override')
        self.DO=[]

        for channel in range(self.NBCHANNEL):
            value=self.valueDigital('do%d' % channel, writable=True)
            self.DO.append(value)
            value.config.set('invert', False)
            value.config.set('default', None)

    def onLoad(self, xml: XMLConfig):
        self.config.xmlUpdateInt(xml, 'watchdog', vmin=0)

        for channel in range(self.NBCHANNEL):
            value=self.DO[channel]

            item=xml.child('do%d' % channel)
            if item:
                if not item.getBool('enable', True):
                    value.disable()
                value.config.xmlUpdateBool(item, 'invert')
                value.config.xmlUpdateBool(item, 'default')

    def poweron(self):
        self.writeRegistersIfChanged(66, self.config.watchdog*100)
        data=0x0
        for channel in range(self.NBCHANNEL):
            value=self.DO[channel]
            state=value.config.default
            if value.config.invert:
                state=not state
            if state:
                data |= (0x1 << channel)
        self.writeRegistersIfChanged(1, data)
        return True

    def poweroff(self):
        return True

    def refresh(self):
        count=self.NBCHANNEL
        r=self.readCoils(0, 2*count)
        if r:
            override=False
            for channel in range(count):
                self.microsleep()
                value=self.DO[channel]

                state=bool(r[channel])
                if value.config.invert:
                    state=not state
                value.updateValue(state)

                state=r[count+channel]
                value.setOverride(state)
                if state:
                    override=True

            self.OVR.updateValue(override)
        return 2.0

    def sync(self):
        for channel in range(self.NBCHANNEL):
            self.microsleep()
            value=self.DO[channel]
            if not value.isEnabled():
                continue
            if value.isPendingSync():
                self.signalRefresh(0.1)
                state=value.toReachValue
                if value.config.invert:
                    state=not state
                if self.writeCoils(channel, state):
                    value.clearSync()

    def off(self):
        for channel in range(self.NBCHANNEL):
            self.DO[channel].off()

    def on(self):
        for channel in range(self.NBCHANNEL):
            self.DO[channel].on()

    def toggle(self):
        for channel in range(self.NBCHANNEL):
            self.DO[channel].toggle()


class MBIODeviceMetzConnectMRDI10(MBIODeviceMetzConnect):
    NBCHANNEL=10

    def onInit(self):
        self.DI=[]
        for channel in range(self.NBCHANNEL):
            value=self.valueDigital('di%d' % channel)
            self.DI.append(value)
            value.config.set('invert', False)

    def onLoad(self, xml: XMLConfig):
        for channel in range(self.NBCHANNEL):
            value=self.DI[channel]
            item=xml.child('di%d' % channel)
            if item:
                if not item.getBool('enable', True):
                    value.disable()
                value.config.xmlUpdateBool(item, 'invert')

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def refresh(self):
        r=self.readDiscreteInputs(0, self.NBCHANNEL)
        if r:
            for channel in range(self.NBCHANNEL):
                self.microsleep()
                value=self.DI[channel]

                state=bool(r[channel])
                if value.config.invert:
                    state=not state

                value.updateValue(state)

        return 1.0


class MBIODeviceMetzConnectMRDI4(MBIODeviceMetzConnectMRDI10):
    NBCHANNEL=4


class MBIODeviceMetzConnectMRAI8(MBIODeviceMetzConnect):
    NBCHANNEL=8

    def getFormatFromType(self, value):
        stype=value.config.type
        types=['pt100', 'pt500', 'pt1000',
            'ni1000-tk5000', 'ni1000-tk6180',
            'balco500',
            'kty81-110', 'kty81-210',
            'ntc-1k8', 'ntc-5k', 'ntc-10k', 'ntc-20k',
            'lm235',
            'ntc-10k-carel']
        try:
            index=types.index(stype.lower())
            value.unit='C'
            return 0x80 | (index << 1) | 0x0
        except:
            pass

        try:
            types=['ohm', '10v']
            index=types.index(stype.lower())
            if index==0:
                value.unit='ohm'
                return (0x2 << 5) | 0x0
            if index==1:
                value.unit='V'
                if value.config.get('unit'):
                    value.unit=value.config.unit
                return (0x0 << 5) | 0x0
        except:
            pass

        self.logger.warning('%s:unknown AI format %s' % (self.key, stype))

        # PT1000
        value.unit='C'
        return 0x80 | (2 << 1) | 0x0

    def onInit(self):
        self.AI=[]
        for channel in range(self.NBCHANNEL):
            value=self.value('ai%d' % channel)
            value.config.set('type', 'pt1000')
            value.config.set('resolution', 0.1)
            value.config.set('offset', 0)
            self.AI.append(value)

    def onLoad(self, xml: XMLConfig):
        for channel in range(self.NBCHANNEL):
            value=self.AI[channel]
            item=xml.child('ai%d' % channel)
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
            value.resolution=value.config.resolution

    def poweron(self):
        for channel in range(self.NBCHANNEL):
            value=self.AI[channel]
            data=self.getFormatFromType(value)
            self.writeRegistersIfChanged(16+channel, data)
        return True

    def poweroff(self):
        return True

    def refresh(self):
        r=self.readInputRegisters(0, self.NBCHANNEL*2)
        if r:
            decoder=self.decoderFromRegisters(r)
            for channel in range(self.NBCHANNEL):
                self.microsleep()
                value=self.AI[channel]
                data=decoder.float32()
                if data is not None:
                    if data<999999:
                        try:
                            dx=(value.config.x1-value.config.x0)
                            data=value.config.x0+data/10.0*dx
                        except:
                            pass

                        value.updateValue(data+value.config.offset)
                        value.setError(False)
                    else:
                        value.updateValue(0)
                        value.setError(True)
        return 5.0


class MBIODeviceMetzConnectMRAOP4(MBIODeviceMetzConnect):
    NBCHANNEL=4

    def onInit(self):
        self.config.set('watchdog', 60)
        self.OVR=self.valueDigital('override')
        self.AO=[]
        for channel in range(4):
            value=self.value('ao%d' % channel, unit='%', writable=True)
            value.setRange(0, 100)
            value.config.set('default', None)
            value.config.set('lrange', 0)
            value.config.set('hrange', 100)
            value.config.set('resolution', 1.0)
            value.config.set('min', 0.0)
            value.config.set('max', 100.0)
            self.AO.append(value)

    def onLoad(self, xml: XMLConfig):
        self.config.xmlUpdateInt(xml, 'watchdog', vmin=0)

        for channel in range(self.NBCHANNEL):
            value=self.AO[channel]

            item=xml.child('ao%d' % channel)
            if item:
                if not item.getBool('enable', True):
                    value.disable()

                value.config.xmlUpdateFloat(item, 'default')
                value.config.xmlUpdateFloat(item, 'lrange', vmin=0, vmax=100)
                value.config.xmlUpdateFloat(item, 'hrange', vmin=value.config.lrange, vmax=100)
                value.config.xmlUpdateFloat(item, 'resolution', vmin=0)
                value.config.xmlUpdateFloat(item, 'min', vmin=0, vmax=100)
                value.config.xmlUpdateFloat(item, 'max', vmin=value.config.min, vmax=100)
            value.resolution=value.config.resolution

    def raw2state(self, value, raw):
        if raw is not None:
            state=raw/0x7fff*100.0
            lrange=value.config.lrange
            hrange=value.config.hrange
            if lrange>0 or hrange<100:
                state=max(lrange, state)
                state=min(hrange, state)
                state=(state-lrange)/(hrange-lrange)*100
            return state

    def state2raw(self, value, state):
        if state is not None:
            lrange=value.config.lrange
            hrange=value.config.hrange
            state=min(state, value.config.max)
            state=max(state, value.config.min)
            if lrange>0 or hrange<100:
                raw=0x7fff/100.0*(lrange+(hrange-lrange)*state/100.0)
            else:
                raw=state/100.0*0x7fff
            return int(raw)

    def poweron(self):
        self.writeRegistersIfChanged(66, self.config.watchdog*100)
        for channel in range(self.NBCHANNEL):
            value=self.AO[channel]
            state=value.config.default
            self.writeRegistersIfChanged(self.NBCHANNEL+channel,
                self.state2raw(value, state))
        return True

    def poweroff(self):
        return True

    def refresh(self):
        count=self.NBCHANNEL
        r=self.readHoldingRegisters(0, count)
        if r:
            for channel in range(count):
                self.microsleep()
                value=self.AO[channel]
                state=self.raw2state(value, r[channel])
                value.updateValue(state)

        r=self.readDiscreteInputs(0, count)
        if r:
            override=False
            for channel in range(count):
                self.microsleep()
                value=self.AO[channel]

                state=r[channel]
                value.setOverride(state)
                if state:
                    override=True

            self.OVR.updateValue(override)
        return 5.0

    def sync(self):
        for channel in range(self.NBCHANNEL):
            self.microsleep()
            value=self.AO[channel]
            if not value.isEnabled():
                continue
            if value.isPendingSync():
                self.signalRefresh(1.0)
                raw=self.state2raw(value, value.toReachValue)
                if self.writeRegisters(channel, raw):
                    value.clearSync()

    def off(self):
        for channel in range(self.NBCHANNEL):
            self.AO[channel].set(0)

    def on(self):
        for channel in range(self.NBCHANNEL):
            self.AO[channel].set(100)

    def toggle(self):
        for channel in range(self.NBCHANNEL):
            if self.AO[channel].value:
                self.AO[channel].set(0)
            else:
                self.AO[channel].set(100)


if __name__ == "__main__":
    pass
