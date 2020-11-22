import re
import sys

import requests
import youtube_dl
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLineEdit, QWidget, QMainWindow, QMessageBox
from qtawesome import icon

from te import CodeEditor


def get_titles(kw):
    videos = set()
    if "https://www.youtube.com/watch?v=" in kw:
        c = 0
        get=False
        while not get and c <= 5:
            try:
                with youtube_dl.YoutubeDL({}) as ydl:
                    video = ydl.extract_info(
                        f'{kw}',
                        download=False  # We just want to extract the info

                    )

                    tg = video.get('tags')
                    if tg:
                        for t in tg:
                            yield t

                    get = True

            except:
                c += 1
        yield "####finish####"

    else:
        url = f'https://www.youtube.com/results?search_query={kw}'
        res = requests.get(url)
        data = res.text

        groupsv = re.findall('"videoId":"[\w]*"', data)
        for gr in groupsv:
            id = gr.split('":"')[1][:-1]
            if len(id) > 3:
                videos.add(f"https://www.youtube.com/watch?v={id}")


        print(videos)
        key_count = 0
        for link in videos:
            counter = 0
            get = False
            while not get and counter <= 2:
                try:
                    with youtube_dl.YoutubeDL({}) as ydl:
                        video = ydl.extract_info(
                            f'{link}',
                            download=False  # We just want to extract the info

                        )

                        tg = video.get('tags')
                        if tg:
                            for t in tg:
                                key_count += 1
                                yield t

                        get = True

                except :
                    counter += 1
        yield "####finish####"


class Worker(QObject):
    keyword = pyqtSignal(str)

    @pyqtSlot(str)
    def get_keyword(self, kw):
        kw_gen = get_titles(kw)
        for k in kw_gen:
            self.keyword.emit(k)


class SEO(QMainWindow):
    keywords_requested = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(SEO, self).__init__(*args, **kwargs)
        la = QVBoxLayout()
        wid = QWidget()
        wid.setLayout(la)
        self.keywords_input = QLineEdit(returnPressed=self.start_keyword, placeholderText="Enter Keyword or video link then "
                                                                                          "press enter")
        la.addWidget(self.keywords_input)
        self.text = CodeEditor()
        la.addWidget(self.text)
        self.setCentralWidget(wid)
        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.keyword.connect(self.add_keyword_to_textedit)
        self.keywords_requested.connect(self.worker.get_keyword)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    def start_keyword(self):
        self.text.clear()
        self.keywords_requested.emit(self.keywords_input.text())

    def add_keyword_to_textedit(self, k):
        if k == "####finish####":
            QMessageBox.information(self, "Finish",
                                    f"we got {self.text.document().blockCount()} keywords | {len(self.text.toPlainText())} chars")
        else:
            self.text.append(f"{k},".strip())


app = QApplication(sys.argv)
win = SEO()
win.setWindowTitle("SEO")
win.setWindowIcon(icon("mdi.google-analytics", color="#4000ff00"))
win.resize(800, 400)
win.show()
sys.exit(app.exec_())

#
