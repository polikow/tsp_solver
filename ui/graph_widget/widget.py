from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5 import QtGui


class GraphWidget(QWidget):
    POINT_SIZE = 25
    POINT_FONT = QFont('Decorative', 12)
    SOLUTION_POINT = QColor(0, 67, 206)
    SOLUTION_EDGE = QPen(QColor(40, 141, 255), 4, Qt.SolidLine)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.sizePolicy().setVerticalPolicy(QSizePolicy.Maximum)
        self.sizePolicy().setHorizontalPolicy(QSizePolicy.Maximum)

        self.solution = None
        self.coordinates = None
        self.draw_all_edges = False
        self.kx = 1
        self.ky = 1
        self.min_x = 0
        self.min_y = 0

    def refresh(self, coordinates=None, solution=None, draw_all_edges=False, x=0, max_x=500, y=0, max_y=500):
        self.coordinates = coordinates
        self.solution = solution
        self.draw_all_edges = draw_all_edges

        if coordinates is not None:
            x = min(coordinates, key=lambda el: el[0])[0]
            max_x = max(coordinates, key=lambda el: el[0])[0]
            y = min(coordinates, key=lambda el: el[1])[1]
            max_y = max(coordinates, key=lambda el: el[1])[1]

        sx = (max_x - x)
        sy = (max_y - y)

        w = self.width()
        h = self.height()

        m = max(sx, sy)
        self.kx = (w * 0.9 / m)
        self.ky = (h * 0.9 / m)

        self.min_x = x
        self.min_y = y

        self.x_shift = w * 0.03
        self.y_shift = h * 0.03

        self.update()

    def calc_x(self, x):
        x = (x - self.min_x) * self.kx
        return x + self.x_shift * self.kx

    def calc_y(self, y):
        y = (y - self.min_y) * self.ky
        return y + self.y_shift * self.ky

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        if self.coordinates is not None:
            if self.draw_all_edges:
                self.draw_edges(qp)
            if self.solution is not None:
                self.draw_solution(qp)
            self.draw_points(qp)
            self.draw_indexes(qp)

        qp.end()

    def draw_points(self, qp):
        size = self.POINT_SIZE
        qp.setPen(self.SOLUTION_POINT)
        qp.setBrush(self.SOLUTION_POINT)

        for x, y in self.coordinates:
            x = self.calc_x(x) - size / 2
            y = self.calc_x(y) - size / 2
            (qp.drawEllipse(x, y, size, size))

    def drawLine(self, qp, i, j):
        x1, y1 = self.coordinates[i]
        x2, y2 = self.coordinates[j]
        x1, y1 = self.calc_x(x1), self.calc_x(y1)
        x2, y2 = self.calc_x(x2), self.calc_x(y2)
        qp.drawLine(x1, y1, x2, y2)

    def draw_edges(self, qp):
        qp.setPen(QPen(Qt.gray, 2, Qt.SolidLine))
        n = len(self.coordinates)
        for i in range(0, n):
            for j in range(i + 1, n):
                if i != j:
                    self.drawLine(qp, i, j)

    def draw_solution(self, qp):
        qp.setPen(self.SOLUTION_EDGE)
        n = len(self.solution)
        for i in range(0, n - 1):
            self.drawLine(qp, self.solution[i], self.solution[i + 1])
        self.drawLine(qp, self.solution[0], self.solution[-1])

    def draw_indexes(self, qp):
        qp.setPen(QPen(Qt.white, 5, Qt.SolidLine))
        qp.setFont(self.POINT_FONT)
        metrics = QtGui.QFontMetrics(self.POINT_FONT)

        for i, (x, y) in enumerate(self.coordinates):
            text = str(i + 1)
            w = metrics.width(text)
            h = metrics.height()
            x = self.calc_x(x) - w / 2 - (1 if len(text) == 2 else 0)
            y = self.calc_x(y) + (self.POINT_SIZE - h * 0.5) / 2
            qp.drawText(x, y, text)
