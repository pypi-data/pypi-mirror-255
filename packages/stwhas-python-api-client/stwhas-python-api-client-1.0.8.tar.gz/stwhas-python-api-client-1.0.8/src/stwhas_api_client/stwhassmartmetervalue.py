from datetime import datetime

class StwHasSmartMeterValue:
    time:datetime = None
    deliveryA:float = 0.0
    deliveryB:float = 0.0
    deliveryMetercountA:float = 0.0
    deliveryMetercountB:float = 0.0
    deliveryMetercountSum:float = 0.0
    deliverySum:float = 0.0
    feedA:float = 0.0
    feedB:float = 0.0
    feedMetercountA:float = 0.0
    feedMetercountB:float = 0.0
    feedMetercountSum:float = 0.0
    feedSum:float = 0.0
    interpolated:bool = False

    def __init__(self, jsonData = None):
        if jsonData != None:
            self.parse(jsonData)

    def fromJson(data):
        return StwHasSmartMeterValue(data)
    
    def parse(self, jsonData):
        self.time = datetime.fromisoformat(jsonData['datetime'])
        for v in [a for a in dir(self) if not a.startswith('__') and a != 'datetime' and a != 'time' and not callable(getattr(self, a))]:
            setattr(self, v, jsonData[v])