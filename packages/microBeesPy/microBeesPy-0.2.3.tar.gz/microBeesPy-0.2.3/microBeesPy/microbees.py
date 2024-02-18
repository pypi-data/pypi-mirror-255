import base64
import aiohttp
import json
from microBeesPy.bee import Bee, Actuator
from microBeesPy.profile import Profile

from microBeesPy.exceptions import MicroBeesException, MicroBeesWrongCredentialsException

class MicroBees :
  token = None
  session = None
  HOST = "https://dev.microbees.com/"
  VERSION = "1_0"
  clientID = None
  clientSecret = None 
  
  def __init__(self,clientID=None,clientSecret=None,session = None, token = None):
    self.session  = aiohttp.ClientSession() if session is None  else  session
    self.clientID = clientID
    self.clientSecret = clientSecret
    self.token = token
  
  async def login(self, username,password,scope="read write"):
    userpass = (
      self.clientID + ":" + self.clientSecret
    )
    auth = base64.b64encode(userpass.encode()).decode()
    data = {
      "username": username,
      "password": password,
      "scope": scope,
      "grant_type": "password",
    }
    headers = {
      "Content-Type": "application/x-www-form-urlencoded",
      "Authorization": "Basic %s" % auth,
    }
    try:
        resp = await self.session.post(self.HOST+"oauth/token",headers = headers, data = data)
        if resp.status == 200:
          response = await resp.text()
          responseObj =  json.loads(response)
          self.token = responseObj.get('access_token')
          return self.token
        else:
          raise MicroBeesWrongCredentialsException("Your username or password is invalid")
    except Exception as e:
      raise e

  async def getBees(self):
    assert self.token is not None, 'Token must be setted'
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % self.token,
    }
    try:
      resp =  await self.session.post(self.HOST+"v/"+self.VERSION+"/getMyBees", headers = headers)
      if resp.status == 200:
        response = await resp.text()
        responseObj =  json.loads(response)
        return [Bee.from_dict(y) for y in responseObj.get("data")]
      else :
        raise MicroBeesException("Error "+str(resp.status))
    except Exception as e:
      raise e

  async def sendCommand(self,actuatorID,relayValue,commandType=6,color=None,temperature=None):
    assert self.token is not None, 'Token must be setted'
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % self.token,
    }
    data = {
      "actuatorID": actuatorID,
      "command_type": commandType,
      "data": {
        "actuatorID": actuatorID,
        "command_type": commandType,
        "relay_value": relayValue,
        "color": color,
        "temperature": temperature,
      }
    }
    try:
      resp = await self.session.post(self.HOST+"v/"+self.VERSION+"/sendCommand", json = data, headers = headers)
      if resp.status == 200:
        response = await resp.text()
        responseObj =  json.loads(response)
        return responseObj.get('status')==0
      else:
        raise MicroBeesException("Error "+str(resp.status))
    except Exception as e:
      raise e
    
  async def getMyBeesByIds (self, beeIDs):
    assert self.token is not None, 'Token must be setted'
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % self.token,
    }
    data = {
      'ids': beeIDs
    }
    try:
      resp = await self.session.post(self.HOST+"v/"+self.VERSION+"/getMyBeesByIds", json = data, headers = headers)
      if resp.status == 200:
        response = await resp.text()
        responseObj =  json.loads(response)
        return [Bee.from_dict(y) for y in responseObj.get("data")]
      else :
        raise MicroBeesException("Error "+str(resp.status))
    except Exception as e:
      raise e
    
  async def getActuatorById (self, actuatorID):
    assert self.token is not None, 'Token must be setted'
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % self.token,
    }
    data = {
      'id': actuatorID
    }
    try:
      resp = await self.session.post(self.HOST+"v/"+self.VERSION+"/getactuatorstatus", json = data, headers = headers)
      if resp.status == 200:
        response = await resp.text()
        responseObj =  json.loads(response)
        return Actuator.from_dict(responseObj.get("data"))
      else :
        raise MicroBeesException("Error "+str(resp.status))
    except Exception as e:
      raise e
    
  async def getMyProfile (self):
    assert self.token is not None, 'Token must be setted'
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % self.token,
    }
    try:
      resp = await self.session.post(self.HOST+"v/"+self.VERSION+"/getMyProfile", headers = headers)
      if resp.status == 200:
        response = await resp.text()
        responseObj =  json.loads(response)
        return Profile.from_dict(responseObj.get("data"))
      else:
        raise MicroBeesException("Error "+str(resp.status))
    except Exception as e:
      raise e