from .stwhassmartmetervalue import StwHasSmartMeterValue

class StwHasSmartMeterData:
    def __init__(self, jsonData = None):
        self.data:list[StwHasSmartMeterValue] = []
        self.unit = ""
        if jsonData != None:
            self.parse(jsonData)
        pass

    def fromJson(data):
        return StwHasSmartMeterData(data)
    
    def parse(self, jsonData):
        if jsonData["values"] is None:
            raise Exception("Invalid data")
        self.unit = jsonData['unit']
        for value in jsonData["values"]:
            data = StwHasSmartMeterValue.fromJson(value)
            if data.deliverySum > 0:
                self.data.append(data)