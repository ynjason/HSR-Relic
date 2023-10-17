import asyncio
import datetime
from relic_evaluator import HSRRelicEvaluator
from ui.hsr_scanner import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
from scanner import HSRScanner
from enum import Enum
from pynput.keyboard import Key, Listener
from helper_functions import resource_path, save_to_json, executable_path
import pytesseract
import sys
import pyuac


pytesseract.pytesseract.tesseract_cmd = resource_path(".\\tesseract\\tesseract.exe")

class IncrementType(Enum):
    LIGHT_CONE_ADD = 0
    LIGHT_CONE_SUCCESS = 100
    RELIC_ADD = 1
    RELIC_SUCCESS = 101
    CHARACTER_ADD = 2
    CHARACTER_SUCCESS = 102


class HSRScannerUI(QtWidgets.QMainWindow, Ui_MainWindow):
    is_scanning = False
    is_evaluating = False

    def __init__(self):
        super().__init__()
        self._scanner_thread = None
        self._listener = InterruptListener()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.pushButtonStartScan.clicked.connect(self.start_scan)
        global debug
        if debug:
            self.lineEditOutputLocation.setText(resource_path("StarRailData"))
            self.lineEditEvaluateOutputLocation.setText(resource_path("StarRailData"))
            # self.lineEditEvaluateInputLocation.setText(resource_path("StarRailData"))
        else:
            self.lineEditOutputLocation.setText(executable_path("StarRailData"))
            self.lineEditEvaluateOutputLocation.setText(executable_path("StarRailData"))
            # self.lineEditEvaluateInputLocation.setText(executable_path("StarRailData"))
        self.tabWidget.setCurrentIndex(0)
        self.spinBoxCharacterNumber.setValue(4)
        self.pushButtonChangeLocation.clicked.connect(self.change_output_location)
        self.pushButtonOpenLocation.clicked.connect(self.open_output_location)
        self.pushButtonChangeEvaluateInputLocation.clicked.connect(self.change_evaluate_input_location)
        self.pushButtonEvaluateChangeLocation.clicked.connect(self.change_evaluate_output_location)
        self.pushButtonStartEvaluate.clicked.connect(self.start_evaluate)

    def change_output_location(self):
        new_output_location = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Location", self.lineEditOutputLocation.text()
        )
        if new_output_location:
            self.lineEditOutputLocation.setText(new_output_location)

    def change_evaluate_output_location(self):
        new_output_location = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Location", self.lineEditEvaluateOutputLocation.text()
        )
        if new_output_location:
            self.lineEditEvaluateOutputLocation.setText(new_output_location)

    def change_evaluate_input_location(self):
        new_input_location = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Input Location", self.lineEditEvaluateInputLocation.text(), "json (*.json)"
        )
        if new_input_location:
            self.lineEditEvaluateInputLocation.setText(new_input_location[0])

    def open_output_location(self):
        output_location = self.lineEditOutputLocation.text()
        if output_location:
            try:
                QtGui.QDesktopServices.openUrl(
                    QtCore.QUrl.fromLocalFile(output_location)
                )
            except Exception as e:
                self.log(f"Error opening output location: {e}")

    def open_evaluate_output_location(self):
        output_location = self.lineEditEvaluateOutputLocation.text()
        if output_location:
            try:
                QtGui.QDesktopServices.openUrl(
                    QtCore.QUrl.fromLocalFile(output_location)
                )
            except Exception as e:
                self.log(f"Error opening output location: {e}")

    def start_scan(self):
        self.disable_start_scan_button()
        for label in [
            self.labelLightConeCount,
            self.labelRelicCount,
            self.labelCharacterCount,
            self.labelLightConeProcessed,
            self.labelRelicProcessed,
            self.labelCharacterProcessed,
        ]:
            label.setText("0")
        self.textEditLog.clear()

        try:
            scanner = HSRScanner(self.get_config())
        except Exception as e:
            self.log(e)
            self.enable_start_scan_button()
            return

        self._scanner_thread = ScannerThread(scanner)

        self._scanner_thread.log.connect(self.log)

        self._scanner_thread.update_progress.connect(self.increment_progress)

        # self._scanner_thread.result.connect(self.log)
        self._scanner_thread.result.connect(self.handle_result)
        self._scanner_thread.result.connect(self._scanner_thread.deleteLater)
        self._scanner_thread.result.connect(self.enable_start_scan_button)
        self._scanner_thread.result.connect(self._listener.stop)

        self._scanner_thread.error.connect(self.log)
        self._scanner_thread.error.connect(self._scanner_thread.deleteLater)
        self._scanner_thread.error.connect(self.enable_start_scan_button)
        self._scanner_thread.error.connect(self._listener.stop)

        self._listener.interrupt.connect(self._scanner_thread.interrupt_scan)
        self._scanner_thread.start()
        self._listener.start()

    def start_evaluate(self):
        self.disable_start_evaluate_button()
        self.textEditEvaluateLog.clear()

        try:
            evaluator = HSRRelicEvaluator(self.get_config())
        except Exception as e:
            self.evaluate_log(e)
            self.enable_start_evaluate_button()
            return

        self._evaluator_thread = EvaluatorThread(evaluator)

        self._evaluator_thread.log.connect(self.evaluate_log)

        self._evaluator_thread.update_progress.connect(self.increment_progress)

        self._evaluator_thread.result.connect(self.handle_evaluate_result)
        self._evaluator_thread.result.connect(self._evaluator_thread.deleteLater)
        self._evaluator_thread.result.connect(self.enable_start_evaluate_button)
        self._evaluator_thread.result.connect(self._listener.stop)

        self._evaluator_thread.error.connect(self.evaluate_log)
        self._evaluator_thread.error.connect(self._evaluator_thread.deleteLater)
        self._evaluator_thread.error.connect(self.enable_start_evaluate_button)
        self._evaluator_thread.error.connect(self._listener.stop)

        self._listener.interrupt.connect(self._evaluator_thread.interrupt_scan)
        self._evaluator_thread.start()
        self._listener.start()

    def get_config(self):
        config = {}
        config["scan_light_cones"] = self.checkBoxScanLightCones.isChecked()
        config["scan_relics"] = self.checkBoxScanRelics.isChecked()
        config["scan_characters"] = self.checkBoxScanChars.isChecked()
        config["scan_character_relics"] = self.checkBoxScanCharRelics.isChecked()
        config["cursor_testing"] = self.checkBoxCursorTesting.isChecked()
        config["scan_character_relics_numbers"] = self.spinBoxCharacterNumber.value()
        config["relic_evaluate_input_path"] = self.lineEditEvaluateInputLocation.text()
        config["filters"] = {
            "light_cone": {
                "min_level": self.spinBoxLightConeMinLevel.value(),
                "min_rarity": self.spinBoxLightConeMinRarity.value(),
            },
            "relic": {
                "min_level": self.spinBoxRelicMinLevel.value(),
                "min_rarity": self.spinBoxRelicMinRarity.value(),
            },
        }
        return config

    def handle_result(self, data):
        output_location = self.lineEditOutputLocation.text()
        file_name = f"HSRScanData_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_to_json(data, output_location, file_name)
        self.log("Scan complete. Data saved to " + output_location)

    def handle_evaluate_result(self, data):
        output_location = self.lineEditEvaluateOutputLocation.text()
        file_name = f"HSREvaluateData_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_to_json(data, output_location, file_name)
        self.evaluate_log("Scan complete. Data saved to " + output_location)

    def increment_progress(self, enum):
        switch = IncrementType(enum)
        if switch == IncrementType.LIGHT_CONE_ADD:
            self.labelLightConeCount.setText(
                str(int(self.labelLightConeCount.text()) + 1)
            )
        elif switch == IncrementType.RELIC_ADD:
            self.labelRelicCount.setText(str(int(self.labelRelicCount.text()) + 1))
        elif switch == IncrementType.CHARACTER_ADD:
            self.labelCharacterCount.setText(
                str(int(self.labelCharacterCount.text()) + 1)
            )
        elif switch == IncrementType.LIGHT_CONE_SUCCESS:
            self.labelLightConeProcessed.setText(
                str(int(self.labelLightConeProcessed.text()) + 1)
            )
        elif switch == IncrementType.RELIC_SUCCESS:
            self.labelRelicProcessed.setText(
                str(int(self.labelRelicProcessed.text()) + 1)
            )
        elif switch == IncrementType.CHARACTER_SUCCESS:
            self.labelCharacterProcessed.setText(
                str(int(self.labelCharacterProcessed.text()) + 1)
            )

    def disable_start_scan_button(self):
        self.is_scanning = True
        self.pushButtonStartScan.setText("Processing...")
        self.pushButtonStartScan.setEnabled(False)

    def enable_start_scan_button(self):
        self.is_scanning = False
        self.pushButtonStartScan.setText("Start Scan")
        self.pushButtonStartScan.setEnabled(True)

    def disable_start_evaluate_button(self):
        self.is_evaluating = True
        self.pushButtonStartEvaluate.setText("Processing...")
        self.pushButtonStartEvaluate.setEnabled(False)

    def enable_start_evaluate_button(self):
        self.is_evaluating = False
        self.pushButtonStartEvaluate.setText("Evaluate")
        self.pushButtonStartEvaluate.setEnabled(True)

    def log(self, message):
        self.textEditLog.appendPlainText(str(message))

    def evaluate_log(self, message):
        self.textEditEvaluateLog.appendPlainText(str(message))

    def setupButtonStartScan(self):
        self.pushButtonStartScan.clicked.connect(self.start_scan)


class InterruptListener(QtCore.QThread):
    interrupt = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = None

    def run(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            self.listener = listener
            listener.join()

    def stop(self):
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        if key == Key.enter:
            self.interrupt.emit()

    def on_release(self, key):
        if key == Key.enter:
            return False


class ScannerThread(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(int)
    result = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(object)
    log = QtCore.pyqtSignal(str)

    def __init__(self, scanner):
        super().__init__()
        self._scanner = scanner
        self._scanner.update_progress = self.update_progress
        self._scanner.logger = self.log

        self._interrupt_requested = False

    def run(self):
        try:
            res = asyncio.run(self._scanner.start_scan())
            # print(res)
            if self._interrupt_requested:
                self.error.emit("Scan interrupted")
            else:
                self.result.emit(res)
        except Exception as e:
            self.error.emit("Scan aborted with error: " + str(e))

    def interrupt_scan(self):
        self._interrupt_requested = True
        self._scanner.stop_scan()

class EvaluatorThread(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(int)
    result = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(object)
    log = QtCore.pyqtSignal(str)

    def __init__(self, _evaluator):
        super().__init__()
        self._evaluator = _evaluator
        self._evaluator.update_progress = self.update_progress
        self._evaluator.logger = self.log

        self._interrupt_requested = False

    def run(self):
        try:
            res = asyncio.run(self._evaluator.start_evaluation())
            # print(res)
            if self._interrupt_requested:
                self.error.emit("Evaluate interrupted")
            else:
                self.result.emit(res)
        except Exception as e:
            self.error.emit("Evaluate aborted with error: " + str(e))

    def interrupt_scan(self):
        self._interrupt_requested = True
        self._evaluator.stop_evaluation()

if __name__ == "__main__":
    import sys

    global debug
    debug = False
    if len(sys.argv) == 2:
        debug = sys.argv[1].lower() == "true"

    if debug and not pyuac.isUserAdmin():
        print("Re-launching as admin!")
        pyuac.runAsAdmin()
    else:        
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(resource_path("images\\app.ico")))
        MainWindow = QtWidgets.QMainWindow()
        ui = HSRScannerUI()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec())

    
