# -*- coding: utf-8 -*-

import sys
from time import sleep
from pywhatkit import search
from win32api import ShellExecute

from PyQt5.QtCore import QThread, pyqtSignal, QRect, QMetaObject, QCoreApplication
from PyQt5.QtWidgets import QLabel, QTextBrowser, QScrollArea, QTextEdit, QPushButton, QWidget, QApplication
from PyQt5.QtGui import QMovie

from gtts import gTTS
from playsound import playsound
from speech_recognition import Microphone, Recognizer


class Salexa:
    def speak(self, text):
        language = "en"
        output = gTTS(text=text, lang=language, slow=False)
        output.save("./sounds/output.mp3")
        playsound("./sounds/output.mp3")
        return text

    def get_audio(self):
        recorder = Recognizer()
        with Microphone() as source:
            playsound("./sounds/alert.mp3")  # alert sound start speaking
            recorder.adjust_for_ambient_noise(source)
            audio = recorder.listen(source)
            playsound("./sounds/alert.mp3")  # alert sound end speaking
            print("Processing...")
            text = recorder.recognize_google(audio)
            print(f"You said:{text}")
        return text


    def start(self):
        text = "I'm Salexa,how can I help you?"
        self.speak(text)
        print(text)
        return text

    def run(self, text):
        if "play" in text.lower() and "music" in text.lower():
            rtext = self.case_music()
        elif "notepad" in text.lower():
            rtext = self.case_notepad()
        elif "stop" in text.lower() or "exit" in text.lower():
            rtext = self.case_exit()
        else:
            rtext = self.case_search(text)
        return rtext

    def case_music(self):
        text = "OK! Here it is!"
        self.speak(text)
        ShellExecute(0, 'open', 'music.mp3', '', '', 1)
        return text

    def case_notepad(self):
        text = "OK! Just opened!"
        self.speak(text)
        ShellExecute(0, 'open', 'notepad.exe', '', '', 1)
        return text

    def case_search(self, text):
        stext = "Here's what I found"
        self.speak(stext)
        search(text.replace("search for", ""))
        return stext

    def case_exit(self):
        text = "Fine, see you next time!"
        self.speak(text)
        return text


class MyThread(QThread):
    text_signal = pyqtSignal(str)
    gif_signal = pyqtSignal(str)
    salexa = Salexa()

    def __init__(self):
        super().__init__()

    def run(self):
        s_words = "Salexa: "
        u_words = " -Me- : "
        while True:
            # Send a signal to replace the GIF every event
            text = s_words + "I'm Salexa,how can I help you?"
            self.gif_signal.emit("icon/play.gif")
            self.text_signal.emit(text)
            self.salexa.start()

            self.text_signal.emit("---------------Speaking--------------")
            self.gif_signal.emit("icon/listen.gif")
            cmd = self.salexa.get_audio()
            self.text_signal.emit(u_words + cmd)

            self.text_signal.emit("--------------Processing-------------")
            self.gif_signal.emit("icon/loading.gif")
            sleep(3)

            self.gif_signal.emit("icon/play.gif")
            text = self.salexa.run(cmd)
            self.text_signal.emit(s_words + text)

            if text == "Fine, see you next time!":
                self.gif_signal.emit("icon/normal.gif")
                break

            self.text_signal.emit("")
            self.gif_signal.emit("icon/normal.gif")
            sleep(3)


class UI_Form(object):

    def process(self):
        self.thread = MyThread()
        self.thread.text_signal.connect(self.textEdit.append)
        self.thread.gif_signal.connect(self.change_gif)
        self.thread.start()

    def change_gif(self, str):
        self.gif.stop()
        self.gif = QMovie(str)
        self.label.setMovie(self.gif)
        self.gif.start()

    def setup_ui(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(500, 800)
        Form.setStyleSheet("background-color: rgb(0, 0, 0);")

        # gif label(changeable)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(150, 20, 171, 161))
        self.gif = QMovie("icon/normal.gif")
        self.label.setMovie(self.gif)
        self.gif.start()

        # Prompt box
        self.textBrowser = QTextBrowser(Form)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(40, 200, 411, 141))

        # Conversation box
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(40, 350, 411, 411))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background-color: black; color: white;font-size: 20px;")
        self.scrollArea.verticalScrollBar().setStyleSheet(
            "QScrollBar:vertical {background-color: black; color: white;}")

        # Text box
        self.textEdit = QTextEdit(self.scrollArea)
        self.textEdit.setGeometry(QRect(0, 0, 409, 409))
        self.textEdit.setPlainText("")

        self.scrollArea.setWidget(self.textEdit)

        # Start button
        self.pushButton_Start = QPushButton("<b>Start</b>", Form)
        self.pushButton_Start.setObjectName(u"pushButton")
        self.pushButton_Start.setGeometry(QRect(100, 767, 90, 25))
        self.pushButton_Start.setStyleSheet("background-color: #4169E1; color: white;font-size: 20px;")
        self.pushButton_Start.clicked.connect(self.process)

        # Exit button
        self.pushButton_Exit = QPushButton("<b>Exit</b>", Form)
        self.pushButton_Exit.setObjectName(u"pushButton")
        self.pushButton_Exit.setGeometry(QRect(300, 767, 90, 25))
        self.pushButton_Exit.setStyleSheet("background-color: #4169E1; color: white;font-size: 20px;")
        self.pushButton_Exit.clicked.connect(QApplication.quit)

        self.retranslate_ui(Form)
        QMetaObject.connectSlotsByName(Form)
        # setup_ui

    def retranslate_ui(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Salexa", None))
        self.label.setText("")
        self.textBrowser.setHtml(QCoreApplication.translate("Form",
                                                            u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                            "p, li { white-space: pre-wrap; }\n"
                                                            "</style></head><body style=\" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600; color:#55aaff;\">You can ask me in these ways:</span></p>\n"
                                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; color:#55aaff;\">---------------------------------------------------------------</span></p>\n"
                                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:"
                                                            "12pt; color:#55aaff;\">Play Music</span></p>\n"
                                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; color:#55aaff;\">Open NotePad</span></p>\n"
                                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; color:#55aaff;\">Search For How To Relax</span></p>\n"
                                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; color:#55aaff;\">Tell Me Something About Harry Potter</span></p></body></html>",
                                                            None))
        self.pushButton_Exit.setText(QCoreApplication.translate("Form", u"Exit", None))
        self.pushButton_Start.setText(QCoreApplication.translate("Form", u"Start", None))
        # retranslateUi


class MyWindow(QWidget, UI_Form):
    def __init__(self):
        super().__init__()
        self.setup_ui(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
