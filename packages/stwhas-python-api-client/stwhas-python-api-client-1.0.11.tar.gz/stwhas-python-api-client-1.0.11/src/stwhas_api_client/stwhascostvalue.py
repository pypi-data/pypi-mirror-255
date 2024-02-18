from datetime import datetime, timezone
from .stwhasinterval import StwhasInterval

from pytz import timezone

class StwHasCostValue:
    def __init__(self, jsonData = None, interval:StwhasInterval = None):
        self.time:datetime = None
        self.interval:StwhasInterval = interval
        self.baseprice:float = 0.0
        self.workprice:float = 0.0
        self.delivery:float = 0.0
        self.sum:float = 0.0
        self.interpolated:bool = False

        if jsonData != None:
            self.parse(jsonData)

    def fromJson(data, interval:StwhasInterval):
        return StwHasCostValue(data, interval)
    
    def parse(self, jsonData):
        self.time = datetime.fromisoformat(jsonData['datetime'])
        ber = timezone('Europe/Berlin')
        self.time = ber.localize(self.time)
        for v in [a for a in dir(self) if not a.startswith('__') and a != 'datetime' and a != 'time' and a != 'interval' and not callable(getattr(self, a))]:
            try:
                setattr(self, v, jsonData[v])
            except:
                pass