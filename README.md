# IoT for Smart Gardening
![Python Version](https://img.shields.io/badge/python-3-informational?style=flat-square) 
![GitHub](https://img.shields.io/github/contributors/iotprojectMPEG/mainproject?style=flat-square)
![GitHub](https://img.shields.io/github/license/iotprojectMPEG/mainproject?style=flat-square)

Internet of Things project for smart gardening.
## Info
### University
* Politecnico di Torino / Polytechnic University of Turin

![](http://www.politocomunica.polito.it/var/politocomunica/storage/images/media/images/marchio_logotipo_politecnico/1371-1-ita-IT/marchio_logotipo_politecnico_medium.jpg)
### Course
* Master of Science program in **ICT for Smart Societies**
* 01QWRBH - **Programming for IoT applications**

<img src="https://didattica.polito.it/zxd/cms_data/image/6/ICT4SS_AzarSHABANI_Matr204782.jpg" width="200" />

## Getting started
### Tools
- Python 3 environment
- MQTT message broker
### Configuration
* Install required python packages in you virtual environment:
``` sh
pip3 install -r requirements.txt
```
* Rename the [api.json.example](https://github.com/iotprojectMPEG/mainproject/blob/master/catalog/api.json.example) in api.json:
``` sh
mv catalog/api.json.example catalog/api.json
```
* You can set all IP addresses, ports and Telegram token by running [set-ip.py](https://github.com/iotprojectMPEG/mainproject/blob/master/set-ip.py) and following the instructions on screen:
``` sh
./set-ip-py
```
* Add gardens, plants and devices to your resource catalog by manually editing  json files or by running:
``` sh
./interface/interface.py
```
* Go to [Sensors installation](https://github.com/iotprojectMPEG/mainproject/blob/master/README.md#sensors-installation) in order to setup your sensors.
### Run
#### Catalog
``` sh
./catalog/catalog.py
```

#### ThingSpeak adaptor
``` sh
./thingspeak/thingspeak.py
```

#### Sensors
* Run all scripts of your [sensors](https://github.com/iotprojectMPEG/mainproject/tree/master/sensors).

#### Strategies
* Run [all your strategies](https://github.com/iotprojectMPEG/mainproject/tree/master/control).

#### Telegram bot
``` sh
./telegram-bot/bot.py
```

#### Freeboard
``` sh
./freeboard/freeboard.py
```

## Sensors installation
### Temperature and humidity sensor (DHT11)
<img src="https://github.com/iotprojectMPEG/mainproject/blob/master/sensors/images/dht11.png" width="500" />

### Rain sensor
<img src="https://github.com/iotprojectMPEG/mainproject/blob/master/sensors/images/rain.jpg" width="500" />

### Light sensor
<img src="https://github.com/iotprojectMPEG/mainproject/blob/master/sensors/images/light.jpg" width="400" /> 


## Team
- Fassio Edoardo  
- Grasso Paolo  
- Maffei Marzia  
- Rende Gennaro  

## License
[GPL-3.0](./LICENSE)
