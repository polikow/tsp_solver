import os

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QSizePolicy

from utils.io import trace


class MapWidget(QWebEngineView):
    map_error_signal = pyqtSignal(str)  # проблема при загрузке карты
    map_loaded_signal = pyqtSignal()  # все готово к работе

    marker_added_signal = pyqtSignal()  #
    marker_removed_signal = pyqtSignal()  #

    matrix_loaded_signal = pyqtSignal()  # матрица расстояний загружена
    matrix_error_signal = pyqtSignal(str)  # ошибка при загрузке матрицы

    is_ready = False
    is_matrix_relevant = False

    def __init__(self, parent=None):
        super(MapWidget, self).__init__(parent)

        self.sizePolicy().setVerticalPolicy(QSizePolicy.Maximum)
        self.sizePolicy().setHorizontalPolicy(QSizePolicy.Maximum)

        # настройки chromium
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)

        # для взаимодествия с Qt из js
        channel = QWebChannel(self)
        self.page().setWebChannel(channel)
        channel.registerObject("handler", self)

        self.markers = []  # [{"lat": ..., "lng": ...}, ...]
        self.matrix = []
        self.solution = None
        self.secondary = None
        self.precise = None

        try:
            map_html_path = f"{os.path.realpath(__file__)}/generated/map.html"
            file = open(map_html_path, 'r')
            html = file.read()
            file.close()
            self.setHtml(html)
        except Exception as e:
            print(e)
            raise Exception(f"failed to read map.html from \"{map_html_path}\"")

        self.loadFinished.connect(self._loaded)

    @trace
    def saved_lat_long(self, saved, callback):
        self.markers = saved
        self.is_matrix_relevant = True
        self.js(f'loadSaved({saved})', lambda _: callback())

    def draw_path(self, solution, secondary=False, precise=False):
        if self.solution == solution and self.secondary == secondary and self.precise == precise:
            return

        self.solution = solution
        self.secondary = secondary
        self.precise = precise

        if self.solution is None:
            return

        self._draw_path()

    @trace
    def _draw_path(self):
        self.js(f"drawPath({list(self.solution)},"
                f"{'true' if self.secondary else 'false'},"
                f"{'true' if self.precise else 'false'})")

    @trace
    @pyqtSlot()
    def load_matrix(self):
        self.js('loadMatrix()')

    @trace
    @pyqtSlot(float, float)
    def _marker_added(self, lat, lng):
        self.js('markersToPoints()', self._marker_added_callback)

    def _marker_added_callback(self, markers):
        self.markers = markers
        self.is_matrix_relevant = False
        self.marker_added_signal.emit()

    @trace
    @pyqtSlot()
    def _marker_removed(self):
        self.js('markersToPoints()', self._marker_removed_callback)

    def _marker_removed_callback(self, markers):
        self.markers = markers
        self.is_matrix_relevant = False
        self.marker_removed_signal.emit()

    @trace
    @pyqtSlot(list)
    def _matrix_loaded(self, matrix):
        self.matrix = matrix
        self.is_matrix_relevant = True
        self.matrix_loaded_signal.emit()

    @trace
    @pyqtSlot(str)
    def _error_loading_matrix(self, error):
        self.matrix_error_signal.emit(error)

    @trace
    def _loaded(self, ok):
        if ok:
            self.js('status', self._process_status)
        else:
            self._process_status('Ошибка при загрузке виджета')

    @trace
    def _process_status(self, status):
        if status == 'ready':
            self.is_ready = True
            self.map_loaded_signal.emit()
        else:
            self.map_error_signal.emit(status)

    def js(self, code, callback=None):
        if callback is None:
            self.page().runJavaScript(code)
        else:
            self.page().runJavaScript(code, callback)
