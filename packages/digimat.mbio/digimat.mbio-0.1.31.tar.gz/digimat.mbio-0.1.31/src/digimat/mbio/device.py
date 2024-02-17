#!/bin/python

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mbio import MBIO
    from .gateway import MBIOGateway

import time
import threading
from prettytable import PrettyTable

from .config import MBIOConfig
from .xmlconfig import XMLConfig

from .items import Items
from .value import MBIOValues, MBIOValue, MBIOValueWritable
from .value import MBIOValueDigital, MBIOValueDigitalWritable
from .value import MBIOValueMultistate, MBIOValueMultistateWritable

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder


class MBIOModbusRegistersEncoder(object):
    def __init__(self, device, encoding=Endian.BIG):
        self._device=device
        self._encoder=BinaryPayloadBuilder(byteorder=encoding, wordorder=encoding)

    def word(self, value):
        self._encoder.add_16bit_uint(value)

    def int(self, value):
        self._encoder.add_16bit_int(value)

    def float16(self, value):
        self._encoder.add_16bit_float(value)

    def float32(self, value):
        self._encoder.add_32bit_float(value)

    def int32(self, value):
        self._encoder.add_32bit_int(value)

    def dword(self, value):
        self._encoder.add_32bit_uint(value)

    def payload(self):
        try:
            return self._encoder.build()
        except:
            pass

    def writeRegisters(self, start):
        return self._device.writeRegisters(start, self.payload())

    def writeRegistersIfChanged(self, start):
        return self._device.writeRegistersIfChanged(start, self.payload())


class MBIOModbusRegistersDecoder(object):
    def __init__(self, r, encoding=Endian.BIG):
        self._decoder=BinaryPayloadDecoder.fromRegisters(r, byteorder=encoding, wordorder=encoding)

    def get(self, vtype):
        try:
            vtype=vtype.lower()
            if vtype=='word':
                return self.word()
            elif vtype=='float32':
                return self.float32()
            elif vtype=='dword':
                return self.dword()
            elif vtype=='int':
                return self.int()
            elif vtype=='int32':
                return self.int32()
            elif vtype=='skip':
                self.word()
                return
            elif vtype=='float16':
                return self.float16()
        except:
            pass

    def word(self):
        try:
            return self._decoder.decode_16bit_uint()
        except:
            pass

    def int(self):
        try:
            return self._decoder.decode_16bit_int()
        except:
            pass

    def float16(self):
        try:
            return self._decoder.decode_16bit_float()
        except:
            pass

    def float32(self):
        try:
            return self._decoder.decode_32bit_float()
        except:
            pass

    def int32(self):
        try:
            return self._decoder.decode_32bit_int()
        except:
            pass

    def dword(self):
        try:
            return self._decoder.decode_32bit_uint()
        except:
            pass


class MBIODevice(object):
    STATE_OFFLINE = 0
    STATE_PROBE = 1
    STATE_POWERON = 2
    STATE_ONLINE = 3
    STATE_POWEROFF = 4
    STATE_ERROR = 5
    STATE_HALT = 6

    def __init__(self, gateway: MBIOGateway, address, xml: XMLConfig = None):
        # assert(isinstance(gateway, MBIOGateway))
        self._gateway=gateway
        self._address=int(address)
        self._key='%s_%d' % (gateway.key, address)
        self._eventReset=threading.Event()
        self._eventHalt=threading.Event()
        self._state=self.STATE_OFFLINE
        self._timeoutState=0
        self._timeoutRefresh=0
        self._timeoutSync=0
        self._timeoutReSync=self.timeout(60)

        # TODO: enable sync after bootup
        self._syncEnable=True
        self._pingRegisterIndex=None
        self._pingRegisterWithHoldingRegister=False
        self._vendor=None
        self._model=None
        self._version=None
        self._error=False
        self._conditionalRegisterWriteCount=0
        self._config=MBIOConfig()

        self._values=MBIOValues(self, self._key, self.logger)
        self._sysvalues=MBIOValues(self, '%s' % self.key, self.logger)

        self._sysComErr=MBIOValueDigital(self._sysvalues, 'comerr')

        self._gateway.devices.add(self)
        self.onInit()
        self.load(xml)

    def onInit(self):
        pass

    def onLoad(self, xml: XMLConfig):
        pass

    def microsleep(self):
        time.sleep(0.001)

    def load(self, xml: XMLConfig):
        if xml:
            try:
                if xml.isConfig('device'):
                    self.onLoad(xml)
            except:
                self.logger.exception('%s:%s:load()' % (self.__class__.__name__, self.key))

    @property
    def key(self):
        return self._key

    @property
    def address(self):
        return self._address

    @property
    def gateway(self) -> MBIOGateway:
        return self._gateway

    @property
    def parent(self):
        return self.gateway

    def getMBIO(self) -> MBIO:
        return self.gateway.getMBIO()

    @property
    def config(self) -> XMLConfig:
        return self._config

    @property
    def values(self):
        return self._values

    @property
    def sysvalues(self):
        return self._sysvalues

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

    @property
    def logger(self):
        return self._gateway.logger

    @property
    def client(self):
        return self._gateway.client

    def enableSync(self):
        self.logger.info('Enable SYNC on device %s' % self._key)
        self._syncEnable=True

    def setPingRegister(self, index, useInputRegister=True):
        self._pingRegisterIndex=index
        self._pingRegisterWithHoldingRegister=not useInputRegister

    def setPingInputRegister(self, index):
        return self.setPingRegister(index, True)

    def setPingHoldingRegister(self, index):
        return self.setPingRegister(index, False)

    def ping(self):
        if self._pingRegisterIndex is not None:
            self.gateway.checkIdleAfterSend()
            if self._pingRegisterWithHoldingRegister:
                if self.readHoldingRegisters(self._pingRegisterIndex) is not None:
                    self.gateway.signalMessageTransmission()
                    return True
            else:
                self.gateway.checkIdleAfterSend()
                if self.readInputRegisters(self._pingRegisterIndex) is not None:
                    self.gateway.signalMessageTransmission()
                    return True
        else:
            self.gateway.checkIdleAfterSend()
            if self.gateway.ping(self.address):
                self.gateway.signalMessageTransmission()
                return True

        self.gateway.signalMessageTransmission()
        self.logger.error('Unable to ping device %s' % self.key)
        return False

    def probe(self):
        return self.gateway.probe(self.address)

    def timeout(self, delay):
        return time.time()+delay

    def isTimeout(self, t):
        if t is None or time.time()>=t:
            return True
        return False

    def isElapsed(self, t, delay):
        if time.time()>=t+delay:
            return True
        return False

    def isOnline(self):
        if self.state==self.STATE_ONLINE:
            return True
        return False

    def isHalted(self):
        if self.state==self.STATE_HALT:
            return True
        return False

    def isError(self):
        if self._error:
            return True
        return False

    def setError(self, state=True):
        if self._error!=state:
            self._error=state
            self._sysComErr.updateValue(state)
            for value in self.values:
                value.setError(state)

    def reset(self):
        self._eventReset.set()

    def halt(self):
        self._eventHalt.set()

    def restartCommunication(self):
        try:
            self.logger.info('Restart device %s communication' % self.key)
            self.gateway.checkIdleAfterSend()
            r=self.client.diag_restart_communication(True, slave=self.address)
            self.gateway.signalMessageTransmission()
            if r and not r.isError():
                return True
        except:
            pass
        self.logger.error('Restart device %s communication' % self.key)
        return False

    @property
    def vendor(self):
        return self._vendor

    @property
    def model(self):
        return self._model

    @property
    def version(self):
        return self._version

    def readDiscreteInputs(self, start, count=1):
        try:
            self.gateway.checkIdleAfterSend()
            r=self.client.read_discrete_inputs(start, count, slave=self.address)
            self.gateway.signalMessageTransmission()
            if r and not r.isError():
                self.signalAlive()
                return r.bits
        except:
            pass
        self.logger.error('<--readDiscretInputs %s:%d#%d' % (self.key, start, count))

    def readCoils(self, start, count=1):
        try:
            self.gateway.checkIdleAfterSend()
            r=self.client.read_coils(start, count, slave=self.address)
            self.gateway.signalMessageTransmission()
            if r and not r.isError():
                self.signalAlive()
                return r.bits
        except:
            pass
        self.logger.error('<--readCoils %s:%d#%d' % (self.key, start, count))

    def writeCoils(self, start, data):
        if data is not None:
            data=self.ensureArray(data)
            try:
                self.gateway.checkIdleAfterSend()
                r=self.client.write_coils(start, data, slave=self.address)
                self.gateway.signalMessageTransmission()
                if r and not r.isError():
                    self.signalAlive()
                    return True
            except:
                pass

        self.logger.error('<--writeCoils %s:%d' % (self.key, start))
        return False

    def readInputRegisters(self, start, count=1):
        try:
            self.gateway.checkIdleAfterSend()
            r=self.client.read_input_registers(start, count, slave=self.address)
            self.gateway.signalMessageTransmission()
            if r and not r.isError():
                self.signalAlive()
                return r.registers
        except:
            pass
        self.logger.error('<--readInputRegisters %s:%d(%X)#%d' % (self.key, start, start, count))

    def readHoldingRegisters(self, start, count=1):
        try:
            self.gateway.checkIdleAfterSend()
            r=self.client.read_holding_registers(start, count, slave=self.address)
            self.gateway.signalMessageTransmission()
            if r and not r.isError():
                self.signalAlive()
                return r.registers
        except:
            pass
        self.logger.error('<--readHoldingRegisters %s:%d(%X)#%d' % (self.key, start, start, count))

    def ensureArray(self, data):
        if data is not None:
            try:
                data[0]
            except:
                # convert to array
                data=[data]
        return data

    def writeRegisters(self, start, data):
        if data is not None:
            data=self.ensureArray(data)
            try:
                self.gateway.checkIdleAfterSend()
                r=self.client.write_registers(start, data, slave=self.address)
                self.gateway.signalMessageTransmission()
                if r and not r.isError():
                    self.signalAlive()
                    return True
            except:
                pass
        self.logger.error('<--writeRegisters %s:%d(0x%X) %s' % (self.key, start, start, str(data)))
        return False

    def writeHoldingRegisters(self, start, data):
        return self.writeRegisters(start, data)

    def resetConditionalRegisterWriteCount(self):
        self._conditionalRegisterWriteCount=0

    def getConditionalRegisterWriteCount(self):
        return self._conditionalRegisterWriteCount

    def writeRegistersIfChanged(self, start, data):
        if data is not None:
            data=self.ensureArray(data)
            size=len(data)
            r=self.readHoldingRegisters(start, size)
            if r:
                for n in range(size):
                    if r[n]!=data[n]:
                        # mismatch, we have to write it
                        self.logger.warning('<--writeRegisters[CauseChanged] %s:%d(0x%X) from %s to %s' %
                            (self.key, start, start, str(r), str(data)))
                        if self.writeRegisters(start, data):
                            self._conditionalRegisterWriteCount+=1
                            return True
                        return False
                # Nothing to change, so it's a success
                return True
        return False

    def decoderFromRegisters(self, r, encoding=Endian.BIG) -> MBIOModbusRegistersDecoder:
        if r:
            try:
                return MBIOModbusRegistersDecoder(r, encoding)
            except:
                pass

    def encoder(self, encoding=Endian.BIG) -> MBIOModbusRegistersEncoder:
        return MBIOModbusRegistersEncoder(self, encoding)

    def poweron(self):
        # to be overriden
        return True

    def poweronsave(self):
        # to be overriden
        # called if any conditional registers write were done during poweron()
        self.logger.debug('Device %s poweron phase has changed some config data!' % (self.key))

    def poweroff(self):
        # to be overriden
        return True

    def sync(self):
        # self.logger.warning('Fallback %s:sync()' % self.key)
        for value in self.values:
            try:
                if value.isPendingSync():
                    self.logger.debug('Fallback default SYNC: clearSync(%s)' % (value))
                    value.clearSync()
            except:
                pass
        return True

    def refresh(self):
        # to be overriden
        return True

    def resync(self, forceRewriteValues=False):
        if self.values.hasWritableValue():
            self.logger.debug('RESYNC device %s' % self.key)
            if forceRewriteValues:
                for value in self.values:
                    if value.isWritable():
                        self.logger.warning('FORCE RESYNC %s' % value)
                        value.signalSync()
            self._timeoutReSync=self.timeout(60)
            self.signalSync()

    def run(self):
        if self.isPendingRefresh(True):
            # self.logger.debug('REFRESH %s#%d' % (self.model, self.address))
            timeout=self.refresh()
            # self.logger.debug('REFRESHDONE %s#%d' % (self.model, self.address))
            if timeout is None:
                timeout=5.0
            self._timeoutRefresh=self.timeout(timeout)

        if self._syncEnable and self.isPendingSync(True):
            # self.logger.debug('SYNC device %s' % self.key)
            self.sync()
            # self.logger.debug('SYNCDONE device %s' % self.key)
            self.signalRefresh()
            self._timeoutReSync=self.timeout(60)
        else:
            if self.isTimeout(self._timeoutReSync):
                self.resync()

        return True

    def signalAlive(self):
        if self._state==self.STATE_ONLINE:
            self._timeoutState=self.timeout(5)

    @property
    def state(self):
        return self._state

    def statestr(self):
        states=['OFFLINE', 'PROBING', 'POWERON', 'ONLINE', 'POWEROFF', 'ERROR', 'HALT']
        try:
            return states[self.state]
        except:
            pass
        return 'UNKNOWN:%d' % self._state

    def updateValuesFlags(self):
        for value in self.values:
            value.updateFlags()

    def setState(self, state, timeout=0):
        if state!=self._state:
            self._state=state
            self.logger.debug('Changing device %s state to %d:%s (T=%ds)' % (self.key,  state, self.statestr(), timeout))
            self._timeoutState=self.timeout(timeout)
            self.updateValuesFlags()

    def manager(self):
        if time.time()>=self._timeoutState:
            timeout=True
        else:
            timeout=False

        # ----------------------------------------------------
        if self._state==self.STATE_ONLINE:
            if timeout:
                if not self.ping():
                    self.setState(self.STATE_ERROR, 5)
                    return
            if self._eventReset.is_set():
                self.setState(self.STATE_OFFLINE, 1)
                return

            if self._eventHalt.is_set():
                self.setState(self.STATE_POWEROFF)
                return

            self.run()
            self.setError(False)
            return

        # ----------------------------------------------------
        elif self._state==self.STATE_OFFLINE:
            if timeout:
                self._eventReset.clear()
                # FIXME: not always supported
                self.restartCommunication()
                self.setState(self.STATE_PROBE)
            return

        # ----------------------------------------------------
        elif self._state==self.STATE_PROBE:
            data=self.probe()
            if data:
                try:
                    if data['vendor']:
                        self._vendor=data['vendor']
                except:
                    pass
                try:
                    if data['model']:
                        self._model=data['model']
                except:
                    pass
                try:
                    if data['version']:
                        self._version=data['version']
                except:
                    pass

            if self.ping():
                self.setState(self.STATE_POWERON)
                return

            self.setState(self.STATE_ERROR, 30)
            return

        # ----------------------------------------------------
        elif self._state==self.STATE_POWERON:
            self.resetConditionalRegisterWriteCount()
            if self.poweron():
                if self.getConditionalRegisterWriteCount()>0:
                    self.logger.debug('Saving updated poweron config of device %s' % self.key)
                    self.poweronsave()
                    self.resync(True)
                self.signalRefresh()
                self.setState(self.STATE_ONLINE, 5)
                return

            self.setState(self.STATE_ERROR, 15)
            return

        # ----------------------------------------------------
        elif self._state==self.STATE_POWEROFF:
            self.poweroff()
            if self._eventHalt.is_set():
                self.setState(self.STATE_HALT)
                return

            self.setState(self.STATE_OFFLINE, 1)
            return

        # ----------------------------------------------------
        elif self._state==self.STATE_ERROR:
            self.setError(True)
            if self._eventHalt.is_set():
                self.setState(self.STATE_HALT)
                return
            if self._eventReset.is_set() or timeout:
                self.setState(self.STATE_OFFLINE, 1)
                return

        # ----------------------------------------------------
        elif self._state==self.STATE_HALT:
            self._eventHalt.clear()
            self.setError(True)
            if self._eventReset.is_set():
                self.setState(self.STATE_OFFLINE, 1)
                return

        # ----------------------------------------------------
        else:
            # self.logger.error('unkown state %d' % self._state)
            self.setState(self.STATE_ERROR, 5)

    def __repr__(self):
        return '%s(%s=%s/%s, %s)' % (self.__class__.__name__, self.key, self.vendor, self.model, self.statestr())

    def dump(self):
        t=PrettyTable()
        t.field_names=['Property', 'Value']
        t.align='l'

        t.add_row(['key', self.key])
        t.add_row(['state', self.statestr()])

        for value in self.values:
            t.add_row([value.key, str(value)])
        for value in self._sysvalues:
            t.add_row([value.key, str(value)])

        print(t.get_string())

    def registerValue(self, value):
        self.gateway.parent.registerValue(value)

    def signalSync(self, delay=0):
        timeout=self.timeout(delay)
        if self._timeoutSync is None or timeout<self._timeoutSync:
            self._timeoutSync=timeout

    def isPendingSync(self, reset=True):
        if self._timeoutSync is not None:
            if self.isTimeout(self._timeoutSync):
                if reset:
                    self._timeoutSync=None
                return True
        return False

    def signalRefresh(self, delay=0):
        timeout=self.timeout(delay)
        if self._timeoutRefresh is None or timeout<self._timeoutRefresh:
            self._timeoutRefresh=timeout

    def isPendingRefresh(self, reset=True):
        if self._timeoutRefresh is not None:
            if self.isTimeout(self._timeoutRefresh):
                if reset:
                    self._timeoutRefresh=None
                return True
        return False

    def off(self):
        pass

    def auto(self):
        for value in self.values:
            value.auto()

    # def manual(self):
        # for value in self.values:
            # value.manual()

    def __getitem__(self, key):
        return self.values[key]


class MBIODeviceGeneric(MBIODevice):
    def onInit(self):
        self._vendor='Generic'
        self._model='Base'
        self.config.set('refreshperiod', 10)
        self.config.set('refresh', None)

    def onLoad(self, xml: XMLConfig):
        self._pingRegisterIndex=xml.getInt('pingInputRegister')
        if self._pingRegisterIndex is None:
            self._pingRegisterIndex=xml.getInt('pingHoldingRegister')
            self._pingRegisterWithHoldingRegister=True

        items=xml.child('values')
        if items:
            for item in items.children('value'):
                writable=item.getBool('writable')
                if item.getBool('digital'):
                    self.valueDigital(item.get('name'), writable=writable)
                else:
                    self.value(item.get('name'), writable=writable)

            for item in items.children('valuedigital'):
                writable=item.getBool('writable')
                self.valueDigital(item.get('name'), writable=writable)

        items=xml.child('refresh')
        if items:
            self.config.set('refreshperiod', items.getInt('period'))
            self.config.set('refresh', items)

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def refresh(self):
        self.logger.warning('%s:refresh()' % self.__class__.__name__)
        items=self.config.refresh
        if items:
            for item in items.children():
                start=item.getInt('start', 0)
                count=item.getInt('count', 1)
                r=None
                if item.tag=='holdingregisters':
                    r=self.readHoldingRegisters(start, count)
                elif item.tag=='inputregisters':
                    r=self.readInputRegisters(start, count)
                decoder=self.decoderFromRegisters(r)
                if decoder:
                    for data in item.children():
                        value=self.values.getByKeyComputedFromName(data.get('target'))
                        if value:
                            try:
                                vdata=decoder.get(data.tag)
                                f=data.getFloat('multiplyby')
                                if f:
                                    vdata*=f
                                f=data.getFloat('divideby')
                                if f:
                                    vdata/=f
                                f=data.getFloat('offset')
                                if f:
                                    vdata+=f
                                value.updateValue(vdata)
                            except:
                                pass
        return self.config.refreshperiod

    def sync(self):
        pass


class MBIODevices(Items):
    def __init__(self, logger):
        super().__init__(logger)
        self._items: list[MBIODevices]=[]
        self._itemByKey={}
        self._itemByAddress={}

    def item(self, key):
        item=self.getByAddress(key)
        if item:
            return item

        item=self.getByKey(key)
        if item:
            return item

    def add(self, item: MBIODevice) -> MBIODevice:
        if isinstance(item, MBIODevice):
            super().add(item)
            self._itemByKey[item.key]=item
            self._itemByAddress[item.address]=item

    def getByKey(self, key):
        try:
            return self._itemByKey[key]
        except:
            pass

    def getByAddress(self, address):
        try:
            return self._itemByAddress[address]
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

    # def dump(self):
        # if not self.isEmpty():
            # t=PrettyTable()
            # t.field_names=['#', 'Address', 'Key', 'Host', 'Open']
            # t.align='l'
            # for item in self._items:
                # t.add_row([self.index(item), item.key, item.host, item.isOpen()])

        # print(t.get_string(sortby="Key"))


if __name__ == "__main__":
    pass
