from datetime import datetime

class StwHasEexValue:
    time:datetime = None
    price:float = 0.0
    interpolated:bool = False

    def __init__(self, jsonData = None):
        if jsonData != None:
            self.parse(jsonData)

    def fromJson(data):
        return StwHasEexValue(data)
    
    def parse(self, jsonData):
        self.time = datetime.fromisoformat(jsonData['datetime'])
        self.price = jsonData['price']
        self.interpolated = jsonData['interpolated']