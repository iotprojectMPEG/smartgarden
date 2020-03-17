#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import requests
import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout
from PyQt5.QtWidgets import QComboBox, QLineEdit, QPushButton, QLabel

CONFIG = 'conf.json'

class Data(object):

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

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Garden")
        self.central_widget = QStackedWidget() 
        self.setCentralWidget(self.central_widget)
        self.setFixedSize(400,175)
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.garden_label = QLabel("Garden name: ")
        self.garden_box = QLineEdit(self)
        self.add_button = QPushButton("Add")
        self.back_button = QPushButton("Back")
        self.grid_layout.addWidget(self.garden_label, 1, 0)
        self.grid_layout.addWidget(self.garden_box, 1, 1)
        self.grid_layout.addWidget(self.add_button, 1, 2)
        self.grid_layout.addWidget(self.back_button, 2, 1)
        self.add_button.clicked.connect(self.posting_garden)

    def added_garden(self):
        added_garden_label = QLabel("Garden %s inserted" %(self.garden_box.text()))
        self.grid_layout.removeWidget(self.garden_label)
        self.garden_label.deleteLater()
        self.garden_label = None
        self.grid_layout.removeWidget(self.garden_box)
        self.garden_box.deleteLater()
        self.garden_box = None
        self.grid_layout.removeWidget(self.add_button)
        self.add_button.deleteLater()
        self.add_button = None
        self.grid_layout.addWidget(added_garden_label, 1, 0)

    def posting_garden(self):
        new_garden = {"name": self.garden_box.text()}
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        cat_url = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/addg"
        self.added_garden()
        return requests.post(cat_url, json.dumps(new_garden))


class AddPlant(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.sel_garden_label = QLabel("Select garden")
        self.garden_combo = QComboBox(self) #dropdown menu
        self.garden_dict = Data().get_gardens()
        for k,v in self.garden_dict.items():#add items to dropdown menu
            self.garden_combo.addItem(k)
        self.plant_label = QLabel("Plant name: ") #text
        self.plant_box = QLineEdit(self) #text box
        self.add_button = QPushButton("Add")
        self.back_button = QPushButton("Back")
        self.grid_layout.addWidget(self.sel_garden_label, 1, 0)
        self.grid_layout.addWidget(self.garden_combo, 1, 1)
        self.grid_layout.addWidget(self.plant_label, 2, 0)
        self.grid_layout.addWidget(self.plant_box, 2, 1)
        self.grid_layout.addWidget(self.add_button, 2, 2)
        self.grid_layout.addWidget(self.back_button, 3, 1)
        self.add_button.clicked.connect(self.posting_plant)

    def added_plant(self):
        added_plant_label = QLabel("Plant %s inserted in garden %s"
                                        %(self.plant_box.text(), str(self.garden_combo.currentText())))
        self.grid_layout.removeWidget(self.sel_garden_label)
        self.sel_garden_label.deleteLater()
        self.sel_garden_label = None
        self.grid_layout.removeWidget(self.garden_combo)
        self.garden_combo.deleteLater()
        self.garden_combo = None
        self.grid_layout.removeWidget(self.plant_label)
        self.plant_label.deleteLater()
        self.plant_label = None
        self.grid_layout.removeWidget(self.plant_box)
        self.plant_box.deleteLater()
        self.plant_box = None
        self.grid_layout.removeWidget(self.add_button)
        self.add_button.deleteLater()
        self.add_button = None
        self.grid_layout.addWidget(added_plant_label, 1, 0)

    def posting_plant(self):
        new_plant = {"gardenID": self.garden_dict[str(self.garden_combo.currentText())],
                    "name": self.plant_box.text()}
        file = open(CONFIG, 'r')
        config = json.load(file)
        file.close()
        cat_url = "http://" + config["cat_ip"] + ":" + config["cat_port"] + "/addp"
        self.added_plant()
        return requests.post(cat_url, json.dumps(new_plant))


class AddDevice(QWidget):
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
        self.add_button = QPushButton("Add")
        self.back_button = QPushButton("Back")
        self.grid_layout.addWidget(self.sel_garden_label, 1, 0)
        self.grid_layout.addWidget(self.garden_combo, 1, 1)
        self.grid_layout.addWidget(self.sel_plant_label, 2, 0)
        self.grid_layout.addWidget(self.plant_combo, 2, 1)
        self.grid_layout.addWidget(self.device_label, 3, 0)
        self.grid_layout.addWidget(self.device_box, 3, 1)
        self.grid_layout.addWidget(self.add_button, 3, 2)
        self.grid_layout.addWidget(self.back_button, 4, 1)
        self.garden_combo.currentIndexChanged.connect(self.plant_drop)
        self.add_button.clicked.connect(self.posting_device)

    def plant_drop(self):
        self.plant_combo.clear()
        self.plant_dict = Data().get_plants(str(self.garden_combo.currentText()))
        for k,v in self.plant_dict.items():
            self.plant_combo.addItem(k)


    def added_device(self):
        added_device_label = QLabel("Device %s of plant %s inserted in garden %s"
                                %(self.device_box.text(), str(self.plant_combo.currentText()),
                                    str(self.garden_combo.currentText())))
        added_device_label.setWordWrap(True)
        self.grid_layout.removeWidget(self.sel_garden_label)
        self.sel_garden_label.deleteLater()
        self.sel_garden_label = None
        self.grid_layout.removeWidget(self.garden_combo)
        self.garden_combo.deleteLater()
        self.garden_combo = None
        self.grid_layout.removeWidget(self.sel_plant_label)
        self.sel_plant_label.deleteLater()
        self.sel_plant_label = None
        self.grid_layout.removeWidget(self.plant_combo)
        self.plant_combo.deleteLater()
        self.plant_combo = None
        self.grid_layout.removeWidget(self.device_label)
        self.device_label.deleteLater()
        self.device_label = None
        self.grid_layout.removeWidget(self.device_box)
        self.device_box.deleteLater()
        self.device_box = None
        self.grid_layout.removeWidget(self.add_button)
        self.add_button.deleteLater()
        self.add_button = None
        self.grid_layout.addWidget(added_device_label, 1, 0)

    def posting_device(self):
        new_device = {"gardenID": self.garden_dict[str(self.garden_combo.currentText())],
                    "plantID": self.plant_dict[str(self.plant_combo.currentText())],
                    "name": self.device_box.text()}
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
