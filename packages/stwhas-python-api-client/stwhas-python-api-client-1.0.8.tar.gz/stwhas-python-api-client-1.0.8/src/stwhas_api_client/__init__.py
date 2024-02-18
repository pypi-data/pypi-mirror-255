from datetime import datetime
from .stwhasinterval import StwhasInterval
from .stwhasunit import StwhasUnit
from .stwhaseexdata import StwHasEexData
from .stwhassmartmeterdata import StwHasSmartMeterData
from .stwhasconsumptioncost import StwHasConsumptionCost
import requests
from pytz import timezone

class StwHasApiClient:
    def __init__(self, username, password, endpoint= 'https://hassfurt.energy-assistant.de/api/') -> None:
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.token = None

    def login(self):
        loginData = {
            "email": self.username,
            "password": self.password
        }
        data = requests.post(self.endpoint + 'auth/v1/customer/login', json=loginData)
        if data.status_code == 200:
            self.token = data.json()["token"]
        return self.token

    def eexData(self, starttime:datetime, endtime:datetime, interval:StwhasInterval, token = None) -> StwHasEexData:
        url = "{endpoint}stockmarket/v1/mapped-values/startdate/{startdate}Z/enddate/{enddate}Z/interval/{interval}".format(
            endpoint=self.endpoint, 
            startdate=starttime.isoformat(), 
            enddate=endtime.isoformat(), 
            interval=interval.value)
        data = self.apiRequest(url, token).json()
        return StwHasEexData.fromJson(data)

    def smartMeterData(self, starttime:datetime, endtime:datetime, meternumber:str, interval:StwhasInterval, token = None) -> StwHasSmartMeterData:
        url = "{endpoint}meter/v1/meters/number/{meternumber}/mapped-values/startdate/{startdate}/enddate/{enddate}/interval/{interval}".format(
            endpoint=self.endpoint, 
            startdate=starttime.isoformat(), 
            enddate=endtime.isoformat(), 
            interval=interval.value,
            meternumber=meternumber)
        data = self.apiRequest(url, token).json()
        return StwHasSmartMeterData.fromJson(data)
    
    # https://hassfurt.energy-assistant.de/api/widget/v1/display/5f3540c8894abb001b7c7f1a/unit/euro/startdate/2023-01-30T00:00:00.000Z/enddate/2023-01-31T00:00:00.000Z/interval/hour/?flow=delivery&dateFormat=HH:00&format=json
    def consumptionCost(self, starttime:datetime, endtime:datetime, interval:StwhasInterval, unit:StwhasUnit, token = None) -> StwHasConsumptionCost:
        starttime = starttime.replace(tzinfo=None)
        endtime = endtime.replace(tzinfo=None)
        utc = timezone("UTC")
        starttime = utc.localize(starttime)
        endtime = utc.localize(endtime)
        url = "{endpoint}widget/v1/display/5f3540c8894abb001b7c7f1a/unit/{unit}/startdate/{startdate}/enddate/{enddate}/interval/{interval}?flow=delivery&dateFormat=YYYY-MM-DDTHH:00:00&format=json".format(
            endpoint=self.endpoint, 
            startdate=starttime.isoformat(), 
            enddate=endtime.isoformat(), 
            interval=interval.value,
            unit=unit.value)
        data = self.apiRequest(url, token).json()
        return StwHasConsumptionCost.fromJson(data, unit, interval)
        
    def apiRequest(self, url, token):
        if token is None and self.token != None:
            token = self.token
        if token == None:
            raise Exception("Please Login first or provide token")
        
        return requests.get(url, headers={
            "Authorization": "Bearer "+token
        })