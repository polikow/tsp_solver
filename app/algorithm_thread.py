from typing import Generator, List

from PyQt5.QtCore import QThread, pyqtSignal


class AlgorithmThread(QThread):
    output = pyqtSignal(tuple)

    def __init__(self, app, algorithm: Generator[int, List[int], float]):
        super().__init__()
        self.app = app
        self.algorithm = algorithm

        app.algorithm_thread = self
        app.algorithm_thread.started.connect(app.algorithm_started)
        app.algorithm_thread.finished.connect(app.algorithm_finished)
        app.algorithm_thread.output.connect(app.show_result)
        app.algorithm_thread.start()

    def run(self):
        try:
            self.app.last = False
            for result in self.algorithm:
                self.output.emit(result)
            self.app.last = True
        except Exception as e:
            self.app.show_error(e)
