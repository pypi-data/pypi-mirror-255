from datetime import datetime

class StwHasEexValue:

    def __init__(self, jsonData = None):
        self.time:datetime = None
        self.price:float = 0.0
        self.interpolated:bool = False
        if jsonData != None:
            self.parse(jsonData)

    def fromJson(data):
        return StwHasEexValue(data)
    
    def parse(self, jsonData):
        self.time = datetime.fromisoformat(jsonData['datetime'])
        self.price = jsonData['price']
        self.interpolated = jsonData['interpolated']