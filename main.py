from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import Qt

from io import BytesIO
import requests
import sys
from itertools import cycle

from map_app import Ui_MainWindow as MainUi
from object_pos import *
from points import *


class Main(QMainWindow, MainUi):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.static_map_request = 'https://static-maps.yandex.ru/1.x/'
        self.current_address = ''
        self.static_map_x = 37.617218
        self.static_map_y = 55.751694
        self.points = []
        self.types_of_map = cycle(["map", "sat", "sat,skl"])
        self.names_of_types_of_map = {"map": "Схема",
                                      "sat": "Спутник",
                                      "sat,skl": "Гибрид"}
        self.static_map_params = {"ll": f'{self.static_map_x},{self.static_map_y}',
                                  "z": '10',
                                  "size": '650,450',
                                  "l": next(self.types_of_map)}
        self.update_image()

        self.map_type_btn.clicked.connect(self.change_type_of_map)
        self.search_btn.clicked.connect(self.set_pos)
        self.reset_btn.clicked.connect(self.reset_search)
        self.index_checkBox.clicked.connect(self.update_address)

    def set_pos(self):
        self.current_address = self.search_lineEdit.text()
        x, y, w, h = get_position(self.current_address)
        self.points.clear()
        self.points.append(point_coords_to_string(x, y))
        self.static_map_x = x
        self.static_map_y = y
        self.update_image()
        self.address_textBrowser.setText(full_address(self.current_address,
                                                      self.index_checkBox.isChecked()))

    def change_type_of_map(self):
        self.static_map_params["l"] = next(self.types_of_map)
        self.map_type_btn.setText(self.names_of_types_of_map[self.static_map_params["l"]])
        self.update_image()

    def update_image(self):
        self.static_map_params["ll"] = f"{self.static_map_x},{self.static_map_y}"
        self.static_map_params["pt"] = list_of_points_to_req_param(self.points)
        response = requests.get(self.static_map_request, params=self.static_map_params)
        self.image = QPixmap()
        try:
            assert self.image.loadFromData(QByteArray(response.content), "PNG")
        except AssertionError:
            self.image.loadFromData(QByteArray(response.content), "JPEG")
        self.map_label.setPixmap(self.image)

    def move_map(self, move_x, move_y):
        z = int(self.static_map_params["z"])
        dx = 360 / 2 ** z
        dy = 180 / 2 ** z
        self.static_map_x += dx * move_x
        self.static_map_y += dy * move_y
        self.static_map_x = (self.static_map_x + 180) % 360 - 180
        self.static_map_y = min(self.static_map_y, 90)
        self.static_map_y = max(self.static_map_y, -90)

    def reset_search(self):
        self.points.clear()
        self.update_image()
        self.address_textBrowser.setText('')
        self.search_lineEdit.setText('')
        self.current_address = ''

    def update_address(self):
        if self.current_address:
            self.address_textBrowser.setText(full_address(self.current_address,
                                                          self.index_checkBox.isChecked()))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            z = int(self.static_map_params["z"])
            if z - 1 >= 0:
                z -= 1
            self.static_map_params["z"] = str(z)

        if event.key() == Qt.Key_PageUp:
            z = int(self.static_map_params["z"])
            if z + 1 <= 17:
                z += 1
            self.static_map_params["z"] = str(z)

        if event.key() == Qt.Key_A:
            self.move_map(-1, 0)

        if event.key() == Qt.Key_W:
            self.move_map(0, 1)

        if event.key() == Qt.Key_D:
            self.move_map(1, 0)

        if event.key() == Qt.Key_S:
            self.move_map(0, -1)

        self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
