import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QFileDialog, QLabel
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import winsound
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import simpleaudio as sa


class App(QMainWindow):
    
    def __init__(self):
        # Creare fereastra de aplicatie
        super().__init__()
        self.left = 100
        self.top = 100
        self.width = 600
        self.height = 400
        
        self.setWindowTitle("Aplicatie de recunoastere vocala")
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Creare textBox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,30)
        
        # Creare buton de incarcare fisier
        self.button1 = QPushButton('Incarcare fisier', self)
        self.button1.move(300,20)
        self.button1.resize(100,30)
        # adaugarea actiunii butonului => functia uploadFile
        self.button1.clicked.connect(self.uploadFile)
        
        # Creare buton de redare audio
        self.button2 = QPushButton('Redare audio', self)
        self.button2.move(20,70)
        self.button2.resize(100,30)
        # adaugarea actiunii butonului => functia playAudio
        self.button2.clicked.connect(self.playAudio)
        
        # Creare buton de afisare semnal
        self.button3 = QPushButton('Afisare semnal', self)
        self.button3.move(130,70)
        self.button3.resize(100,30)
        # adaugarea actiunii butonului => functia displayAudio
        self.button3.clicked.connect(self.displayAudio)
        
        # Creare buton de pause semnal
        self.button6 = QPushButton('Pauza', self)
        self.button6.move(250,70)
        self.button6.resize(100,30)
        # adaugarea actiunii butonului => functia displayAudio
        self.button6.clicked.connect(self.pauseAudio)
        
         # Creare text
        self.text = QLabel(self)
        self.text.move(20,120)
        self.text.setText('Introduceti momentul de start al unui fonem vocalizat utilizand imaginea semnalului')
        self.text.adjustSize()
        # Creare label
        self.label = QLabel(self)
        self.label.move(20,150)
        self.label.setText('Start fonem (numar intreg):')
        self.label.adjustSize()
        # Creare textBox
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(160, 140)
        self.textbox2.resize(70,30)
        
        # Creare buton de afisare categorie
        self.button4 = QPushButton('Afisare categorie', self)
        self.button4.move(20,190)
        self.button4.resize(110,30)
        # adaugarea actiunii butonului => functia classifyAudio
        self.button4.clicked.connect(self.classifyAudio)
        
         # Creare text decizie
        self.resultText = QLabel(self)
        self.resultText.move(20,230)
            
    
    def uploadFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file','C:\\',"Audio files (*.wav)")
        self.textbox.setText(file_name)
        
    def playAudio(self):
        # winsound.PlaySound(self.textbox.text(), winsound.SND_FILENAME)
        self.wave_obj = sa.WaveObject.from_wave_file(self.textbox.text())
        self.play_obj = self.wave_obj.play()
    def pauseAudio(self):
        print(self.play_obj.stop())
        
    def displayAudio(self):
       _,data = wavfile.read(self.textbox.text())
       data = data / max(abs(data))
       self.figure = plt.figure('semnal')
       self.canvas = FigureCanvas(self.figure)
       self.toolbar = NavigationToolbar(self.canvas, self) 
       self.figure.clear()
       ax = self.figure.add_subplot(111)
       ax.plot(data)
       self.canvas.draw() 
        
    def classifyAudio(self):
        fs,data = wavfile.read(self.textbox.text())
        data = data / max(abs(data))
        N = 20*10**(-3)*fs
        start_a = int(self.textbox2.text())
        stop_a = start_a + N
        a = data[start_a:int(stop_a)]
        #functia de autocorelatie de timp scurt
        Ats = np.correlate(a, a, mode='full')
        peaks, _ = find_peaks(Ats, prominence=1)
        # plt.figure('Ats')
        # plt.plot(Ats)
        # plt.plot(peaks, Ats[peaks], "x")
        # plt.show() 
        if(peaks.size < 2):
            self.resultText.setText('Fonemul ales nu este un fonem vocalizat. Alegeti alt fonem!')
            self.resultText.setFont(QFont('Arial', 10))
            self.resultText.adjustSize()
            return;
        #primul maxim
        max1 = np.argmax(Ats)
        print('max1 = ',max1)

        #alegem al doilea maxim
        max2 = 0
        for i in range(0,len(peaks)):
            if(Ats[peaks[i]] > Ats[max2] and peaks[i] != max1):
                max2 = peaks[i]
        print('max2 = ', max2)
        
        #calculam frecventa fundamentala
        F0 = (1/(abs(max2-max1)))*fs

        if F0 >= 255 and F0 <= 1000:
            self.resultText.setText('Cel mai probabil vorbitorul este copil')
            self.resultText.setFont(QFont('Arial', 10))
            self.resultText.adjustSize()
        elif F0 >= 165:
            self.resultText.setText('Cel mai probabil vorbitorul este de sex feminin')
            self.resultText.setFont(QFont('Arial', 10))
            self.resultText.adjustSize()
        elif F0 >= 85:
            self.resultText.setText('Cel mai probabil vorbitorul este de sex masculin')
            self.resultText.setFont(QFont('Arial', 10))
            self.resultText.adjustSize()
        else:
            self.resultText.setText('Nu s-a putut gasi categoria vorbitorului')
            self.resultText.setFont(QFont('Arial', 10))
            self.resultText.adjustSize()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    ex = App()
    ex.show()
    app.exec_() 