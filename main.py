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

        self.lat = None
        self.lot = None
        self.date = None
        self.time = None

    def update_ports_list(self):
        self.ui.cBox_Ports.clear()
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.ui.cBox_Ports.addItems(ports)

    def portDataReceived(self):
        if self.serialPort.isOpen():
            self.ui.txt_Results.clear()
            data = self.serialPort.readAll().data().decode()
            self.ui.txt_Results.setText(data)
            print(data)
            self.save_data_to_file(data)
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
            with open('serial_data_log.txt', 'a') as dosya:
                dosya.write('******************************************************************************************\n')
                dosya.write('                                   Port Bağlantı Kuruldu!!\n')
                dosya.write('******************************************************************************************\n')

    def save_data_to_file(self, data):
        try:
            parsed_data = None
            lines = data.split('\n')

            self.write_to_file("serial_data_log.txt", data)
            for line in lines:
                parsed_data = self.parse_nmea_sentence(line)
                self.write_to_file("parsed_gnss_data.txt", parsed_data)
                # TODO: Burası sonsuz döngü gibi oluyor sürekli data geliyor ve baştan başlıyor fordan çıkamıyor yani....

            self.write_lat_lon_to_file("lat_lon_data.txt", self.lat, self.lon, self.date, self.time)
            print("Veri dosyaya başarıyla yazıldı.")

        except Exception as e:
            print(f"Dosyaya yazma hatası: {e}")


    # Çıktıyı dosyaya yazma fonksiyonu
    def write_to_file(self, filename, content):
        with open(filename, 'a') as file:
            file.write(content)

    def write_lat_lon_to_file(filename, lat, lon, date, time):
        with open(filename, 'a') as file:  # 'a' modu ile dosyaya ekleme yapar
            file.write(f"Tarih: {date}, Saat: {time}, Enlem: {lat}, Boylam: {lon}\n")

    # Her satırın GNSS tipi ve verilerini parse eden fonksiyon
    def parse_nmea_sentence(self, sentence):
        output = ""
        if sentence.startswith("$"):
            parts = sentence.split(',')
            type_code = parts[0][1:]
            output += f"\nVeri Tipi: {type_code}\n"

            if type_code == "GNRMC":
                output += "- GNRMC: Tavsiye Edilen Minimum Spesifik GPS/Transit Verisi\n"
                output += f"  Zaman (UTC): {parts[1]}\n"
                output += f"  Geçerlilik: {parts[2]}\n"
                output += f"  Enlem: {parts[3]} {parts[4]}\n"
                output += f"  Boylam: {parts[5]} {parts[6]}\n"
                output += f"  Hız (knots): {parts[7]}\n"
                output += f"  Tarih: {parts[9]}\n"

                self.lat = f"{parts[3]} {parts[4]}"
                self.lon = f"{parts[5]} {parts[6]}"
                self.date = parts[9]
                self.time = parts[1]

            elif type_code == "GNVTG":
                output += "- GNVTG: İyi Yapılan Parkur ve Yerdeki Hız\n"
                output += f"  Hız (knots): {parts[5]}\n"
                output += f"  Hız (km/h): {parts[7]}\n"

            elif type_code == "GNGGA":
                output += "- GNGGA: Global Konumlama Sistemi Sabitleme Verisi\n"
                output += f"  Zaman (UTC): {parts[1]}\n"
                output += f"  Enlem: {parts[2]} {parts[3]}\n"
                output += f"  Boylam: {parts[4]} {parts[5]}\n"
                output += f"  Sabitleme Kalitesi: {parts[6]}\n"
                output += f"  Uydu Sayısı: {parts[7]}\n"
                output += f"  HDOP: {parts[8]}\n"
                output += f"  Deniz Seviyesinden Yükseklik: {parts[9]} {parts[10]}\n"

            elif type_code == "GNGSA":
                output += "- GNGSA: GNSS DOP ve Aktif Uydular\n"
                output += f"  Sabitleme Modu: {parts[1]}\n"
                output += f"  PDOP: {parts[-3]}\n"
                output += f"  HDOP: {parts[-2]}\n"
                output += f"  VDOP: {parts[-1].split('*')[0]}\n"

            elif type_code == "GPGSV" or type_code.startswith("GLGSV") or type_code.startswith("GBGSV"):
                output += "- GSV: GNSS Uydu Görünülürlük Bilgisi\n"
                output += f"  Toplam Mesaj Sayısı: {parts[1]}\n"
                output += f"  Mesaj Numarası: {parts[2]}\n"
                output += f"  Toplam Uydu Sayısı: {parts[3]}\n"

            elif type_code == "GNGLL":
                output += "- GNGLL: Coğrafi Konum Bilgisi\n"
                output += f"  Enlem: {parts[1]} {parts[2]}\n"
                output += f"  Boylam: {parts[3]} {parts[4]}\n"
                output += f"  Zaman (UTC): {parts[5]}\n"
                output += f"  Geçerlilik: {parts[6]}\n"

                self.lat = f"{parts[1]} {parts[2]}"
                self.lon = f"{parts[3]} {parts[4]}"
                self.time = parts[5]

        return output


if __name__ == "__main__":
    # Uygulama nesnesi oluşturulur
    app = QtWidgets.QApplication(sys.argv)

    # Ana pencere oluşturulur ve gösterilir
    window = MainWindow()
    window.show()

    # Uygulamanın çalıştırılması
    sys.exit(app.exec_())
