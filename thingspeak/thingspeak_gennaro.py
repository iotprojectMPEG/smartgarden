#!/usr/bin/env python3.7

import requests
import time
request = None
item = None


for count in range(4):
  print('STARTING the program')
  RequestToThingspeak = 'https://api.thingspeak.com/update?api_key=4P7ALDEHKRJ054OI&field1='
  RequestToThingspeak +=str(123)
  request = requests.get(RequestToThingspeak)
  print('Request SENT !')
  print(request.text)
  time.sleep(5)
