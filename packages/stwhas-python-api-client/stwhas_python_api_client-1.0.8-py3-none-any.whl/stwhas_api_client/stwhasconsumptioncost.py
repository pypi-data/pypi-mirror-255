from .stwhascostvalue import StwHasCostValue
from .stwhasunit import StwhasUnit
from .stwhasinterval import StwhasInterval
import os, time, datetime
from datetime import datetime, timezone

class StwHasConsumptionCost:
    data:list[StwHasCostValue] = []
    unit:StwhasUnit = None

    def __init__(self, jsonData = None, unit:StwhasUnit = None, interval:StwhasInterval = None):
        self.unit = unit
        if jsonData != None:
            self.parse(jsonData, interval)
        pass

    def fromJson(data, unit:StwhasUnit, interval:StwhasInterval):
        data = StwHasConsumptionCost(data, unit, interval)
        return data
    
    def parse(self, jsonData, interval:StwhasInterval):
        if jsonData["values"] is None:
            raise Exception("Invalid data")
        for value in jsonData["values"]:
            data = StwHasCostValue.fromJson(value, interval)
            self.data.append(data)