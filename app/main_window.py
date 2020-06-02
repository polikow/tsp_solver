from typing import List, Tuple

from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QMainWindow

from app.algorithm_thread import AlgorithmThread

from ui import *
from utils import *
from algo import *


class App(QMainWindow):
    size = 15
    solution = None
    _coordinates = None
    _graph_matrix = None
    draw_all_edges = True
    algorithm_thread = None
    last = False
    _mode = 'Карта'

    def __init__(self):
        super(App, self).__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        self.mapWidget = MapWidget()
        self.mapWidget.map_loaded_signal.connect(self.map_is_ready)
        self.mapWidget.marker_added_signal.connect(self.state_changed)
        self.mapWidget.marker_removed_signal.connect(self.state_changed)

        self.graphWidget = GraphWidget()
        self.ui.placeholder.addWidget(self.mapWidget)
        self.ui.placeholder.addWidget(self.graphWidget)
        self.ui.placeholder.setCurrentWidget(self.mapWidget)

        self.ui.saveButton.clicked.connect(self.save)
        self.ui.loadButton.clicked.connect(self.load)
        self.ui.generateButton.clicked.connect(self.generate_graph)

        self.ui.buttonRunHGA.clicked.connect(self.run_hybrid)
        self.ui.buttonRunGa.clicked.connect(self.run_ga)
        self.ui.buttonRunPSO.clicked.connect(self.run_pso)

        self.ui.checkBox.stateChanged.connect(self.draw_edges_checkbox_changed)
        self.ui.modeComboBox.currentTextChanged.connect(self.mode_changed)

        self.input_widgets = [
            self.ui.saveButton,
            self.ui.loadButton,
            self.ui.generateButton,
            self.ui.buttonRunHGA,
            self.ui.buttonRunGa,
            self.ui.buttonRunPSO,
        ]

        self.state_changed()

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self._coordinates = coordinates
        self.size = len(coordinates)
        self.solution = None
        self.refresh_coordinates_table()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        self.state_changed()

    @property
    def graph_matrix(self):
        return self._graph_matrix

    @graph_matrix.setter
    def graph_matrix(self, matrix):
        self._graph_matrix = matrix
        self.refresh_adjacency_table()

    @property
    def is_map_ready(self):
        return self.mapWidget.is_ready

    @property
    def algorithm_is_running(self):
        return self.algorithm_thread is not None

    @property
    def lat_long(self):
        return self.mapWidget.markers

    @lat_long.setter
    def lat_long(self, lat_long):
        self.size = len(lat_long)
        self.solution = None
        self.mapWidget.saved_lat_long(lat_long, self.refresh_coordinates_table)

    @property
    def map_matrix(self):
        if self.mapWidget.is_matrix_relevant:
            return self.mapWidget.matrix
        else:
            return None

    @map_matrix.setter
    def map_matrix(self, matrix):
        if matrix is not None:
            self.mapWidget.matrix = matrix
            self.mapWidget.is_matrix_relevant = True
            self.refresh_adjacency_table()

    @trace
    def map_is_ready(self):
        self.state_changed()

    def toggle_save_button(self):
        if self.mode == 'Граф':
            if self.coordinates is None:
                self.ui.saveButton.hide()
            else:
                self.ui.saveButton.show()

        elif self.mode == 'Карта':
            if len(self.lat_long) == 0:
                self.ui.saveButton.hide()
            else:
                self.ui.saveButton.show()

    def toggle_buttons(self):
        if self.mode == 'Карта':
            self.ui.label_7.hide()
            self.ui.lineEdit_6.hide()
            self.ui.generateButton.hide()
            self.ui.placeholder.setCurrentWidget(self.mapWidget)
        elif self.mode == 'Граф':
            self.ui.label_7.show()
            self.ui.lineEdit_6.show()
            self.ui.generateButton.show()
            self.ui.placeholder.setCurrentWidget(self.graphWidget)

    @trace
    def state_changed(self):
        if self.mode == 'Карта' and not self.is_map_ready:
            self.inputs(False)
        elif self.algorithm_is_running:
            self.inputs(False)
        else:
            self.inputs(True)

        if self.mode == 'Карта':
            if self.lat_long is None:
                text = f'Не выбрано'
            elif len(self.lat_long) == 0:
                text = f'Пустая карта'
            else:
                num = len(self.lat_long)
                text = f'Карта ({num} координат)'
            self.ui.currentLabel.setText(text)

        elif self.mode == 'Граф':
            if self.coordinates is None:
                text = f'Не выбрано'
            elif len(self.coordinates) == 0:
                text = f'Пустой граф'
            else:
                num = len(self.coordinates)
                text = f'Граф ({num} вершин)'
            self.ui.currentLabel.setText(text)

        self.toggle_save_button()
        self.toggle_buttons()

    @trace
    def mode_changed(self, new_mode):
        self.mode = new_mode

    @trace
    def run_ga(self):
        try:
            pop_size = int(self.ui.lineEdit_12.text())
            generations = int(self.ui.lineEdit_16.text())
            mutation = float(self.ui.lineEdit_13.text())
        except ValueError:
            return

        if self.mode == 'Граф':
            if self.graph_matrix is None:
                return
            ga = GA(self.graph_matrix, pop_size, generations, mutation)
            AlgorithmThread(self, ga.run())

        elif self.mode == 'Карта':
            context = self

            @trace
            def run():
                context.disconnect_matrix_signals()
                ga = GA(context.mapWidget.matrix, pop_size, generations, mutation)
                AlgorithmThread(context, ga.run())

            @trace
            def error_during_loading(error):
                context.disconnect_matrix_signals()
                context.inputs(True)
                context.ui.textEdit.setText(f'Ошибка при формировании матрицы смежности!\n\n{error}')
                ...

            if self.mapWidget.is_matrix_relevant:
                run()
            else:
                self.inputs(False)
                self.mapWidget.load_matrix()
                self.mapWidget.matrix_loaded_signal.connect(run)
                self.mapWidget.matrix_error_signal.connect(error_during_loading)

    @trace
    def disconnect_matrix_signals(self):
        try:
            self.mapWidget.matrix_loaded_signal.disconnect()
            self.mapWidget.matrix_error_signal.disconnect()
        except TypeError:
            ...

    @trace
    def run_pso(self):
        try:
            pop_size = int(self.ui.lineEdit_15.text())
            iterations = int(self.ui.lineEdit_20.text())
            alpha = float(self.ui.lineEdit_18.text())
            beta = float(self.ui.lineEdit_19.text())
        except ValueError:
            return None

        if self.graph_matrix is None:
            return None

        pso = PSO(self.graph_matrix, pop_size, iterations, alpha, beta)
        AlgorithmThread(self, pso.run())

    @trace
    def run_hybrid(self):
        try:
            pop_size = int(self.ui.lineEdit_7.text())
            generations = int(self.ui.lineEdit_17.text())
            mutation = float(self.ui.lineEdit_8.text())
            iterations = int(self.ui.lineEdit_9.text())
            alpha = float(self.ui.lineEdit_10.text())
            beta = float(self.ui.lineEdit_11.text())
        except ValueError:
            return None

        if self.graph_matrix is None:
            return None

        hga = HybridGA(self.graph_matrix, pop_size, generations, mutation, iterations, alpha, beta)
        AlgorithmThread(self, hga.run())

    def show_result(self, result: Tuple[int, List[int], float]):
        i, self.solution, length = result
        solution = ' - '.join([str(a + 1) for a in self.solution])
        self.ui.textEdit.setText(f'Поколение: {i}\nЛучшее Решение:\n{solution}\n\nДлина пути: {length:.2f}')

    @trace
    def draw_edges_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.draw_all_edges = True
        else:
            self.draw_all_edges = False

    @trace
    def generate_graph(self):
        try:
            size = int(self.ui.lineEdit_6.text())
        except ValueError:
            return None

        self.coordinates = generate_coordinates(size)
        self.graph_matrix = generate_matrix(self.coordinates)

        self.state_changed()

    def paintEvent(self, e):
        if self.mode == 'Граф':
            self.graphWidget.refresh(self.coordinates, self.solution, self.draw_all_edges)
        elif self.mode == 'Карта':
            self.mapWidget.draw_path(self.solution, self.draw_all_edges, self.last)

    @trace
    def inputs(self, value):
        for input_widget in self.input_widgets:
            input_widget.setEnabled(value)

    @trace
    def algorithm_started(self):
        self.inputs(False)

    @trace
    def algorithm_finished(self):
        self.algorithm_thread = None
        self.inputs(True)

    @trace
    def update_params(self, params):
        mode = params['mode']
        coordinates = params.get('coordinates')
        lat_long = params.get('lat_long')
        matrix = params.get('matrix')

        if mode == 'Граф':
            self.coordinates = coordinates
            self.graph_matrix = generate_matrix(coordinates) if matrix is None else matrix

        elif mode == 'Карта':
            self.lat_long = lat_long
            self.map_matrix = matrix

        if self.mode == mode:
            self.state_changed()
        else:
            self.ui.modeComboBox.setCurrentText(mode)

    @trace
    def refresh_adjacency_table(self):
        if self.mode == 'Граф':
            matrix = self.graph_matrix
        elif self.mode == 'Карта':
            matrix = self.map_matrix
        else:
            return

        if matrix is None:
            return

        n = len(matrix)
        cities = [str(i) for i in range(1, n + 1)]
        table = self.ui.tableWidget

        table.setRowCount(n)
        table.setColumnCount(n)
        table.setHorizontalHeaderLabels(cities)
        table.setVerticalHeaderLabels(cities)
        for i in range(0, n):
            table.verticalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)
            table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)

        for i in range(0, n):
            for j in range(0, n):
                if matrix[i][j] == 0:
                    item = QTableWidgetItem('0')
                    item.setBackground(QtGui.QColor(100, 100, 150))
                else:
                    item = QTableWidgetItem(f'{matrix[i][j]:.1f}')
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)

        for i in range(0, n):
            table.setColumnWidth(i, 54)

    @trace
    def refresh_coordinates_table(self):
        if self.mode == 'Граф':
            coordinates = self.coordinates
            headers = ('x', 'y')
        elif self.mode == 'Карта':
            coordinates = [[elem['lat'], elem['lng']] for elem in self.lat_long]
            headers = ('Широта', 'Долгота')
        else:
            return

        if coordinates is None:
            return

        n = len(coordinates)
        table = self.ui.tableWidget_2

        table.setRowCount(n)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
        table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        table.setVerticalHeaderLabels([str(i) for i in range(1, n + 1)])
        for i in range(0, n):
            table.verticalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)

        for i in range(0, n):
            item_x = QTableWidgetItem(f'{coordinates[i][0]}')
            item_y = QTableWidgetItem(f'{coordinates[i][1]}')
            item_x.setTextAlignment(Qt.AlignCenter)
            item_y.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 0, item_x)
            table.setItem(i, 1, item_y)

    def save(self):
        options = QFileDialog.Options()
        try:
            file, _ = QFileDialog.getSaveFileName(self,
                                                  "Сохранить", "./data", "Json file (*.json)",
                                                  options=options)
            if self.mode == 'Граф':
                if self.graph_matrix is None:
                    save(file, dict(mode=self.mode,
                                    coordinates=self.coordinates))
                else:
                    save(file, dict(mode=self.mode,
                                    coordinates=self.coordinates,
                                    matrix=self.graph_matrix))
            elif self.mode == 'Карта':
                if self.map_matrix is None:
                    save(file, dict(mode=self.mode,
                                    lat_long=self.lat_long))
                else:
                    save(file, dict(mode=self.mode,
                                    lat_long=self.lat_long,
                                    matrix=self.map_matrix))
        except Exception as e:
            self.display_error(e)

    def load(self):
        options = QFileDialog.Options()
        try:
            file, _ = QFileDialog.getOpenFileName(self,
                                                  "Загрузить граф...", "./data", "Json file (*.json)",
                                                  options=options)
            params = load(file)
            self.update_params(params)
        except Exception as e:
            self.display_error(e)

    def display_error(self, error):
        print(error)
