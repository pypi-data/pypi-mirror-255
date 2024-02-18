from datetime import datetime
from pytz import timezone

class StwHasSmartMeterValue:

    def __init__(self, jsonData = None):
        self.time:datetime = None
        self.deliveryA:float = 0.0
        self.deliveryB:float = 0.0
        self.deliveryMetercountA:float = 0.0
        self.deliveryMetercountB:float = 0.0
        self.deliveryMetercountSum:float = 0.0
        self.deliverySum:float = 0.0
        self.feedA:float = 0.0
        self.feedB:float = 0.0
        self.feedMetercountA:float = 0.0
        self.feedMetercountB:float = 0.0
        self.feedMetercountSum:float = 0.0
        self.feedSum:float = 0.0
        self.interpolated:bool = False

        if jsonData != None:
            self.parse(jsonData)

    def fromJson(data):
        return StwHasSmartMeterValue(data)
    
    def parse(self, jsonData):
        self.time = datetime.fromisoformat(jsonData['datetime'])
        self.time = self.time.replace(tzinfo=None)
        self.time = timezone("Europe/Berlin").localize(self.time)
        for v in [a for a in dir(self) if not a.startswith('__') and a != 'datetime' and a != 'time' and not callable(getattr(self, a))]:
            setattr(self, v, jsonData[v])