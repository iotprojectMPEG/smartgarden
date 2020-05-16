#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import requests
import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout
from PyQt5.QtWidgets import QComboBox, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore

CONFIG = 'conf.json'

class Data(object):
    """ Get data from catalog """

    def __init__(self):
        return

    def get_gardens(self):
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        string = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/static" #URL for GET
        data = json.loads(requests.get(string).text)  #GET for catalog
        g_names = [g["name"] for g in data["gardens"]] #Generate list of gardens names
        g_ids = [g["gardenID"] for g in data["gardens"]] #Generate list of gardens IDs
        g_dict = dict(zip(g_names, g_ids)) #Generate dictionary of gardens
        return g_dict

    def get_plants(self,garden_name):
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        string = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/static" #URL for GET
        data = json.loads(requests.get(string).text)  #GET for catalog
        for g in data["gardens"]:
            if g["name"] == garden_name:
                p_names = [p["name"] for p in g["plants"]] #Generate list of plants names
                p_ids = [p["plantID"] for p in g["plants"]] #Generate list of plants IDs
        p_dict = dict(zip(p_names, p_ids)) #Generate dictionary of gardens
        return p_dict

    def get_f(self,garden_name,plant_name):
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        string = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/static" #URL for GET
        data = json.loads(requests.get(string).text)  #GET for catalog
        f_list = []
        for g in data["gardens"]:
            if g["name"] == garden_name:
                for p in g["plants"]:
                    if p["name"] == plant_name:
                        for d in p["devices"]:
                            f_list = f_list + [r["f"] for r in d["resources"]]
        if not f_list:
            f_max = 0
        else:
            f_max = max(f_list)
        return f_max

class MainWindow(QMainWindow):
    """ Set up interface main window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Garden")
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.setFixedSize(520,350)
        self.start_window()

    def start_window(self):
        self.addThings_widget = AddThings(self)
        self.addThings_widget.garden_button.clicked.connect(self.adding_garden)
        self.addThings_widget.plant_button.clicked.connect(self.adding_plant)
        self.addThings_widget.device_button.clicked.connect(self.adding_device)
        self.central_widget.addWidget(self.addThings_widget)
        self.central_widget.setCurrentWidget(self.addThings_widget)

    def adding_garden(self):
        self.add_garden_widget = AddGarden(self)
        self.central_widget.addWidget(self.add_garden_widget)
        self.central_widget.setCurrentWidget(self.add_garden_widget)
        self.add_garden_widget.back_button.clicked.connect(self.start_window)

    def adding_plant(self):
        self.add_plant_widget = AddPlant(self)
        self.central_widget.addWidget(self.add_plant_widget)
        self.central_widget.setCurrentWidget(self.add_plant_widget)
        self.add_plant_widget.back_button.clicked.connect(self.start_window)

    def adding_device(self):
        self.add_device_widget = AddDevice(self)
        self.central_widget.addWidget(self.add_device_widget)
        self.central_widget.setCurrentWidget(self.add_device_widget)
        self.add_device_widget.back_button.clicked.connect(self.start_window)


class AddThings(QWidget):
    """ First window layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)

        self.garden_button = QPushButton('Add Garden')
        self.plant_button = QPushButton('Add Plant')
        self.device_button = QPushButton('Add device')

        self.grid_layout.addWidget(self.garden_button, 1, 0)
        self.grid_layout.addWidget(self.plant_button, 1, 1)
        self.grid_layout.addWidget(self.device_button, 1, 2)

class AddGarden(QWidget):
    """ Layout of add garden window """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.garden_label = QLabel("Garden name: ")
        self.garden_box = QLineEdit(self)
        self.location_label = QLabel("Garden location: ")
        self.location_box = QLineEdit(self)
        self.add_button = QPushButton("Add")
        self.back_button = QPushButton("Back")
        self.grid_layout.addWidget(self.garden_label, 1, 0)
        self.grid_layout.addWidget(self.garden_box, 1, 1)
        self.grid_layout.addWidget(self.location_label, 2, 0)
        self.grid_layout.addWidget(self.location_box, 2, 1)
        self.grid_layout.addWidget(self.add_button, 3, 1)
        self.grid_layout.addWidget(self.back_button, 4, 1)
        self.add_button.clicked.connect(self.posting_garden)

    def added_garden(self):
        added_garden_label = QLabel("Garden %s inserted" %(self.garden_box.text()))
        for cnt in reversed(range(self.grid_layout.count()-1)):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
        # self.grid_layout.removeWidget(self.garden_label)
        # self.garden_label.deleteLater()
        # self.garden_label = None
        # self.grid_layout.removeWidget(self.garden_box)
        # self.garden_box.deleteLater()
        # self.garden_box = None
        # self.grid_layout.removeWidget(self.location_label)
        # self.location_label.deleteLater()
        # self.location_label = None
        # self.grid_layout.removeWidget(self.location_box)
        # self.location_box.deleteLater()
        # self.location_box = None
        # self.grid_layout.removeWidget(self.add_button)
        # self.add_button.deleteLater()
        # self.add_button = None
        self.grid_layout.addWidget(added_garden_label, 1, 0, 1, -1)

    def posting_garden(self):
        new_garden = {"name": self.garden_box.text(),
                    "location": self.location_box.text()}
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        cat_url = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/addg"
        self.added_garden()
        return requests.post(cat_url, json.dumps(new_garden))


class AddPlant(QWidget):
    """ Layout of add plant window """

    def __init__(self, parent=None):
        super().__init__(parent)
        m_hours = ["%.2d" % i for i in range(0,12)]
        e_hours = ["%.2d" % i for i in range(12,24)]
        minutes = ["%.2d" % i for i in range(0,60,10)]
        self.grid_layout = QGridLayout(self)
        self.sel_garden_label = QLabel("Select garden")
        self.garden_combo = QComboBox() #dropdown menu
        self.garden_dict = Data().get_gardens()
        for k,v in self.garden_dict.items():#add items to dropdown menu
            self.garden_combo.addItem(k)
        self.plant_label = QLabel("Plant name: ") #text
        self.plant_box = QLineEdit() #text box
        self.water_label = QLabel("Water")
        self.water_box = QLineEdit()
        self.humidity_label = QLabel("Humidity")
        self.humidity_box = QLineEdit()
        self.morning_label = QLabel("Morning irrigation")
        self.morning_hour = QComboBox()
        self.morning_min = QComboBox()
        #self.morning_box = QLineEdit()
        self.evening_label = QLabel("Evening irrigation")
        self.evening_hour = QComboBox()
        self.evening_min = QComboBox()
        #self.evening_box = QLineEdit()
        for i in m_hours:
            self.morning_hour.addItem(i)
        for i in e_hours:
            self.evening_hour.addItem(i)
        for i in minutes:
            self.morning_min.addItem(i)
            self.evening_min.addItem(i)
        self.thingspeak_label = QLabel("Thingspeak ID")
        self.thingspeak_box = QLineEdit()
        self.add_button = QPushButton("Add")
        self.back_button = QPushButton("Back")
        self.grid_layout.addWidget(self.sel_garden_label, 1, 0)
        self.grid_layout.addWidget(self.garden_combo, 1, 1, 1, -1)
        self.grid_layout.addWidget(self.plant_label, 2, 0)
        self.grid_layout.addWidget(self.plant_box, 2, 1, 1, -1)
        self.grid_layout.addWidget(self.water_label, 3, 0)
        self.grid_layout.addWidget(self.water_box, 3, 1, 1, -1)
        self.grid_layout.addWidget(self.humidity_label, 4, 0)
        self.grid_layout.addWidget(self.humidity_box, 4, 1, 1, -1)
        self.grid_layout.addWidget(self.morning_label, 5, 0)
        self.grid_layout.addWidget(self.morning_hour, 5, 1)
        self.grid_layout.addWidget(self.morning_min, 5, 2)
        #self.grid_layout.addWidget(self.morning_box, 5, 1)
        self.grid_layout.addWidget(self.evening_label, 6, 0)
        self.grid_layout.addWidget(self.evening_hour, 6, 1)
        self.grid_layout.addWidget(self.evening_min, 6, 2)
        #self.grid_layout.addWidget(self.evening_box, 6, 1)
        self.grid_layout.addWidget(self.thingspeak_label, 7, 0)
        self.grid_layout.addWidget(self.thingspeak_box, 7, 1, 1, -1)
        self.grid_layout.addWidget(self.add_button, 8, 1, 1, -1)
        self.grid_layout.addWidget(self.back_button, 9, 1, 1, -1)
        self.add_button.clicked.connect(self.posting_plant)

    def added_plant(self):
        added_plant_label = QLabel("Plant %s inserted in garden %s"
                                    %(self.plant_box.text(), str(self.garden_combo.currentText())))
        for cnt in reversed(range(self.grid_layout.count()-1)):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
        self.grid_layout.addWidget(added_plant_label, 1, 0, 1, -1)

    def posting_plant(self):
        m_time = self.morning_hour.currentText() + ':' + self.morning_min.currentText()
        e_time = self.evening_hour.currentText() + ':' + self.evening_min.currentText()
        new_plant = {"gardenID": self.garden_dict[str(self.garden_combo.currentText())],
                    "name": self.plant_box.text(),
                    "hours": [{"time": m_time, "type": "morning"},
                            {"time": e_time, "type": "evening"}],
                    "thingspeakID": int(self.thingspeak_box.text()),
                    "env":{"water": int(self.water_box.text()), "humidity": int(self.humidity_box.text())}}
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        cat_url = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/addp"
        self.added_plant()
        return requests.post(cat_url, json.dumps(new_plant))


class AddDevice(QWidget):
    """ Layout of add device window """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.back_button = QPushButton("Back")
        self.sel_garden_label = QLabel("Select garden")
        self.garden_combo = QComboBox(self)
        self.garden_dict = Data().get_gardens()
        for k,v in self.garden_dict.items():
            self.garden_combo.addItem(k)
        self.sel_plant_label = QLabel("Select plant")
        self.plant_combo = QComboBox(self)
        self.plant_dict = Data().get_plants(str(self.garden_combo.currentText()))
        for k,v in self.plant_dict.items():
            self.plant_combo.addItem(k)
        self.device_label = QLabel("Device name: ") #text
        self.device_box = QLineEdit(self) #text box
        self.resource_label = QLabel("Resources") #text
        self.resource_button = QPushButton("New resource")
        self.add_button = QPushButton("Add")
        self.back_button = QPushButton("Back")
        self.grid_layout.addWidget(self.sel_garden_label, 1, 0)
        self.grid_layout.addWidget(self.garden_combo, 1, 1)
        self.grid_layout.addWidget(self.sel_plant_label, 2, 0)
        self.grid_layout.addWidget(self.plant_combo, 2, 1)
        self.grid_layout.addWidget(self.device_label, 3, 0)
        self.grid_layout.addWidget(self.device_box, 3, 1)
        self.ly_widget = QWidget()
        self.sublayout = QGridLayout(self.ly_widget)
        #self.sublayout = QGridLayout()
        self.grid_layout.addWidget(self.resource_label, 4, 0)
        self.grid_layout.addWidget(self.resource_button, 4, 1, 1, 1, alignment=QtCore.Qt.AlignHCenter)
        self.grid_layout.addWidget(self.ly_widget, 5, 1, 1, -1)
        #self.grid_layout.addLayout(self.sublayout, 5, 0, 1, -1)
        idx = self.grid_layout.indexOf(self.ly_widget)
        location = self.grid_layout.getItemPosition(idx)
        self.grid_layout.addWidget(self.add_button, location[0]+1, 1)
        self.grid_layout.addWidget(self.back_button, location[0]+2, 1)
        self.garden_combo.currentIndexChanged.connect(self.plant_drop)
        self.resource_button.clicked.connect(self.new_resource)
        self.add_button.clicked.connect(self.posting_device)

    def plant_drop(self):
        self.plant_combo.clear()
        self.plant_dict = Data().get_plants(str(self.garden_combo.currentText()))
        for k,v in self.plant_dict.items():
            self.plant_combo.addItem(k)

    def new_resource(self):
        resource_list = ["humidity", "irrigation", "light", "rain", "temperature", "wind"]
        self.resource_combo = QComboBox(self) #text box
        for i in resource_list:
            self.resource_combo.addItem(i)
        row_idx = self.sublayout.rowCount()
        self.sublayout.addWidget(self.resource_combo, row_idx+1, 0, 1, 1, alignment=QtCore.Qt.AlignHCenter)


    def added_device(self):
        added_device_label = QLabel("Device %s of plant %s inserted in garden %s"
                                %(self.device_box.text(), str(self.plant_combo.currentText()),
                                    str(self.garden_combo.currentText())))
        added_device_label.setWordWrap(True)
        for cnt in reversed(range(self.grid_layout.count()-1)):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
        self.grid_layout.addWidget(added_device_label, 1, 0, 1, -1)

    def posting_device(self):
        resource_measure = {"humidity": "%", "irrigation": "n.a.", "light": "lm",
                            "rain": "(bool)", "temperature": "Celsius", "wind": "kn"}
        f_val = Data().get_f(str(self.garden_combo.currentText()),str(self.plant_combo.currentText()))
        add_resources = []
        for cnt in reversed(range(self.sublayout.count())):
            widget = self.sublayout.takeAt(cnt).widget()
            if widget is not None:
                f_val += 1
                res_dict = {"n": widget.currentText(),
                                "u": resource_measure[widget.currentText()], "f": f_val}
                add_resources.append(res_dict)
        new_device = {"gardenID": self.garden_dict[str(self.garden_combo.currentText())],
                    "plantID": self.plant_dict[str(self.plant_combo.currentText())],
                    "name": self.device_box.text(),
                    "resources": add_resources}
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        cat_url = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/addd"
        self.added_device()
        return requests.post(cat_url, json.dumps(new_device))


if __name__=='__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
