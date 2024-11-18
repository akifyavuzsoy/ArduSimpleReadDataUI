import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from mainUI import Ui_MainWindow  # main.ui ile oluşturulmuş py dosyanız


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.serial_thread = None

        self.serialPort = QSerialPort()

        # Connect button click event
        self.ui.btn_ReadData.clicked.connect(self.portConnect)
        self.ui.tBtn_UpdatePorts.clicked.connect(self.update_ports_list)
        self.serialPort.readyRead.connect(self.portDataReceived)

        # Initially update the ports list
        self.update_ports_list()

    def update_ports_list(self):
        self.ui.cBox_Ports.clear()
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.ui.cBox_Ports.addItems(ports)

    def portDataReceived(self):
        if self.serialPort.isOpen():
            self.ui.txt_Results.clear()
            self.ui.txt_Results.setText(self.serialPort.readAll().data().decode())
            #self.ui.txt_Results.append(self.serialPort.readAll().data().decode())

    def portDisconnect(self):
        if self.serialPort.isOpen():
            self.serialPort.close()
            self.pushButtonConnect.setEnabled(True)
            self.pushButtonDisconnect.setEnabled(False)
            self.pushButtonSend.setEnabled(False)

    def portConnect(self):
        self.serialPort.setPortName(self.ui.cBox_Ports.currentText())
        self.serialPort.setBaudRate(int(self.ui.cBox_BaudRates.currentText()))
        self.serialPort.setDataBits(QSerialPort.Data8)
        self.serialPort.setParity(QSerialPort.EvenParity)
        self.serialPort.setStopBits(QSerialPort.OneStop)
        if not self.serialPort.isOpen():
            self.serialPort.open(QIODevice.ReadWrite)



if __name__ == "__main__":
    # Uygulama nesnesi oluşturulur
    app = QtWidgets.QApplication(sys.argv)

    # Ana pencere oluşturulur ve gösterilir
    window = MainWindow()
    window.show()

    # Uygulamanın çalıştırılması
    sys.exit(app.exec_())
