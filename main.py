import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from mainUI import Ui_MainWindow  # main.ui ile oluşturulmuş py dosyanız

import threading
import queue
import time
from datetime import datetime, timedelta

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

        self.readDataBuf = []

        self.lat = None
        self.lon = None
        self.date = None
        self.time = None

        self.processor_thread = None
        self.data_queue = queue.Queue()  # Veri kuyruğu
        self.stop_event = threading.Event()  # Thread'leri durdurmak için
        self.output_file = "lat_lon_data.txt"

    def update_ports_list(self):
        self.ui.cBox_Ports.clear()
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.ui.cBox_Ports.addItems(ports)

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

    def portDataReceived(self):
        if self.serialPort.isOpen():
            self.ui.txt_Results.clear()
            data = self.serialPort.readAll().data().decode()
            self.readDataBuf.append(data)
            self.ui.txt_Results.setText(data)
            self.data_queue.put(data)
            print(data)
            #self.save_data_to_file(data)
            #self.ui.txt_Results.append(self.serialPort.readAll().data().decode())

    def save_data_to_file(self):
        while not self.stop_event.is_set():
            try:
                parsed_data = None
                nmea_sentence = self.data_queue.get(timeout=1)
                lines = [line.split('\n') for line in nmea_sentence]
                print("******************", lines)
                self.write_to_file("serial_data_log.txt", nmea_sentence)
                parsed_data = self.parse_nmea_sentence(nmea_sentence)
                self.write_to_file("parsed_gnss_data.txt", parsed_data)
                # TODO: Burası sonsuz döngü gibi oluyor sürekli data geliyor ve baştan başlıyor fordan çıkamıyor yani....

                self.write_lat_lon_to_file("lat_lon_data.txt", self.lat, self.lon, self.date, self.time)
                self.readDataBuf.clear()
                print("Veri dosyaya başarıyla yazıldı.")


            except queue.Empty:
                # Kuyruk boşsa bir şey yapma, devam et
                pass


    # Çıktıyı dosyaya yazma fonksiyonu
    def write_to_file(self, filename, content):
        with open(filename, 'a') as file:
            file.write(content)

    def write_lat_lon_to_file(self, filename, lat, lon, date=None, time=None):
        # Tarih ve saat formatlama
        formatted_date = None
        if date:
            try:
                formatted_date = datetime.strptime(date, "%d%m%y").strftime("%d %B %Y")
            except ValueError:
                formatted_date = "Geçersiz Tarih"

            # Saat formatlama ve +3 saat ekleme
        formatted_time = None
        if time:
            try:
                # Zamanı parçala ve +3 saat ekle
                raw_time = datetime.strptime(time[:6], "%H%M%S")
                adjusted_time = raw_time + timedelta(hours=3)
                formatted_time = adjusted_time.strftime("%H:%M:%S")
            except (ValueError, IndexError):
                formatted_time = "Geçersiz Saat"

        # Enlem ve boylam formatlama
        try:
            # Enlem ve boylam yön bilgilerini ayrıştır
            lat_value, lat_dir = lat.split()
            lon_value, lon_dir = lon.split()

            # Enlem dönüşümü
            lat_degrees = int(float(lat_value) // 100)
            lat_minutes = float(lat_value) % 100
            lat_decimal = lat_degrees + (lat_minutes / 60)
            if lat_dir == "S":  # Güney yarım küre negatif
                lat_decimal = -lat_decimal

            # Boylam dönüşümü
            lon_degrees = int(float(lon_value) // 100)
            lon_minutes = float(lon_value) % 100
            lon_decimal = lon_degrees + (lon_minutes / 60)
            if lon_dir == "W":  # Batı yarım küre negatif
                lon_decimal = -lon_decimal

        except ValueError:
            lat_decimal = "Geçersiz Enlem"
            lon_decimal = "Geçersiz Boylam"

        # Formatlanmış veri yazımı
        with open(filename, 'a') as file:
            file.write(
                f"Tarih: {formatted_date if formatted_date else 'Bilinmiyor'}, "
                f"Saat: {formatted_time if formatted_time else 'Bilinmiyor'}, "
                f"Enlem: {lat_decimal if isinstance(lat_decimal, float) else lat_decimal}, "
                f"Boylam: {lon_decimal if isinstance(lon_decimal, float) else lon_decimal}\n"
            )

    # Her satırın GNSS tipi ve verilerini parse eden fonksiyon
    def parse_nmea_sentence(self, sentence):
        output = ""
        if sentence[0].startswith("$"):
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

    def start_thread(self):
        """
        Thread'leri başlatır.
        """
        self.processor_thread = threading.Thread(target=self.save_data_to_file)
        self.processor_thread.daemon = True  # GUI kapandığında thread sonlansın
        self.processor_thread.start()

    def stop_thread(self):
        """
        Thread'leri durdurur.
        """
        self.stop_event.set()
        self.processor_thread.join()


if __name__ == "__main__":
    # Uygulama nesnesi oluşturulur
    app = QtWidgets.QApplication(sys.argv)
    # Ana pencere oluşturulur ve gösterilir
    window = MainWindow()
    try:
        # Thread başlatılır
        window.start_thread()
        window.show()
        # Uygulamanın çalıştırılması
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print("Durduruluyor...")
        window.stop_thread()