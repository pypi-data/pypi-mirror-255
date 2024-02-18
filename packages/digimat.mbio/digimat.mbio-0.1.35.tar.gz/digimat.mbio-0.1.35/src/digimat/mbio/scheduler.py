from __future__ import annotations
from typing import TYPE_CHECKING

from functools import total_ordering

from datetime import datetime
import csv


@total_ordering
class Trigger(object):
    def __init__(self, dow: str, t: str, state: bool = True, sp=None):
        self._dow=str(dow).lower()
        self._state=bool(state)
        self._sp=sp
        self._h=None
        self._m=None
        self._stamp=None
        self.parseTime(t)

    @property
    def dow(self):
        return self._dow

    @property
    def h(self):
        return self._h

    @property
    def m(self):
        return self._m

    @property
    def stamp(self):
        return self._stamp

    @property
    def state(self):
        return self._state

    @property
    def sp(self):
        return self._sp

    def t(self, offset=0):
        stamp=self.stamp+offset
        return '%02d:%02d' % (stamp // 3600, stamp % 3600)

    def parseTime(self, t):
        try:
            t=str(t).replace('h', ':')
            if ':' in t:
                items=list(t.split(':'))
                self._h=int(items[0])
                self._m=int(items[1])
                if self._m is None:
                    self._m=0
            else:
                self._h=int(t)
                self._m=0

            self._stamp=self._h*60+self._m
        except:
            pass

    def matchDow(self, date=None):
        try:
            if self._h is not None and self._m is not None:
                if not date:
                    date=datetime.now()
                dow=date.weekday()
                if str(dow) in self._dow:
                    return True
                if '*' in self._dow:
                    return True
                if dow in [6, 7] and self._dow=='we':
                    return True
                if dow<6 and self._dow=='wd':
                    return True
        except:
            pass
        return False

    def __eq__(self, other):
        if self.stamp==other.stamp:
            if self.dow==other.dow:
                return True
        return False

    def __lt__(self, other):
        if self.stamp==other.stamp:
            if self.dow=='*' and other.dow!='*':
                return True
            if self.dow!='*' and other.dow=='*':
                return False
            if len(self.dow)>len(other.dow):
                return True
            return False
        if self.stamp<other.stamp:
            return True
        return False


class Scheduler(object):
    def __init__(self, name, sp=None):
        self._triggers=[]
        self._name=name
        self._sp=sp
        self._sorted=False

    def reset(self):
        self._triggers=[]
        self._sorted=False

    @property
    def name(self):
        return self._name

    def now(self):
        return datetime.now()

    def dow(self, date):
        return

    def addTrigger(self, trigger: Trigger):
        if trigger is not None:
            self._triggers.append(trigger)
            self._sorted=False
            return trigger

    def on(self, dow: str, t: str, sp=None):
        try:
            return self.addTrigger(Trigger(dow, t, state=True, sp=sp))
        except:
            pass

    def off(self, dow: str, t: str, sp=None):
        try:
            return self.addTrigger(Trigger(dow, t, state=False, sp=sp))
        except:
            pass

    def slot(self, dow: str, t: str, duration: int, sp=None):
        try:
            t0=Trigger(dow, t, state=True, sp=sp)
            t1=Trigger(dow, t0.t(duration), state=False)
            self.addTrigger(t0)
            self.addTrigger(t1)
            return t0, t1
        except:
            pass

    def eval(self, date: datetime = None):
        if not self._sorted:
            self._triggers.sort()
            self._sorted=True

        state=False
        sp=self._sp
        if date is None:
            date=self.now()
        stamp=date.hour*60+date.minute
        if date is not None:
            for t in self._triggers:
                if t.matchDow(date):
                    if stamp>=t.stamp:
                        state=t.state
                        if t.sp is not None:
                            sp=t.sp
                    else:
                        # Triggers are sorted
                        break
        return state, sp


class Schedulers(object):
    def __init__(self):
        self._schedulers={}

    def get(self, name):
        try:
            return self._schedulers[name.lower()]
        except:
            pass

    def __getitem__(self, key):
        return self.get(key)

    def __iter__(self):
        return iter(self._schedulers.values())

    def create(self, name, sp=None):
        scheduler=self.get(name)
        if not scheduler:
            scheduler=Scheduler(name, sp)
            self._schedulers[name.lower()]=scheduler
        return scheduler

    def eval(self, name, date=None):
        try:
            return self.get(name).eval(date)
        except:
            pass

    def loadcsv(self, fpath, delimiter=',', dialect='unix'):
        with open(fpath) as csvfile:
            reader=csv.reader(csvfile, delimiter=delimiter, dialect=dialect)
            for row in reader:
                print(row)


if __name__ == '__main__':
    pass
