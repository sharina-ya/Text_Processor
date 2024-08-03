import sys
import webbrowser

import click
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QLabel, QMenuBar,
                             QMenu, QAction, QTextEdit, QScrollArea, QFileDialog,
                             QMessageBox, QFontComboBox, QComboBox, QSizePolicy, QInputDialog, QTextBrowser)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QUrl


class Processor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Текстовый процессор")
        self.text_fied = QTextEdit(self)
        self.text_fied.setFont(QFont("Times New Roman", 14))

        scroll = QScrollArea(self)
        scroll.setWidget(self.text_fied)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(500)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.show()

        self.setCentralWidget(scroll)
        self.create_menu_bar()
        self.pages = []
        self.page_number = 1
        self.lines = 45
        self.change_pages()
        self.page_label = QLabel(f"Страница {self.page_number}", self)
        self.page_label.setAlignment(Qt.AlignRight)
        self.page_label.move(600, 550)
        self.cur_line = 0


    def create_menu_bar(self):
        menubar = QMenuBar(self)
        menu = QMenu("Файл", menubar)
        menu.addAction(QAction("Новый", self, triggered=self.new_file))
        menu.addSeparator()
        menu.addAction(QAction("Открыть", self, triggered=self.open_file))
        menu.addSeparator()
        menu.addAction(QAction("Сохранить", self, triggered=self.save_file))
        menu.addSeparator()
        menu.addAction(QAction("Выход", self, triggered=self.close))
        menubar.addMenu(menu)
        formatter = QMenu("Формат", menubar)
        formatter.addAction(QAction("Жирный", self, triggered=self.to_bold))
        formatter.addAction(QAction("Курсив", self, triggered=self.to_italic))
        formatter.addAction(QAction("Подчеркивание", self, triggered=self.to_underline))
        formatter.addSeparator()

        self.all_fonts = QFontComboBox(self)
        self.all_fonts.currentFontChanged.connect(self.change_font)

        formatter.addAction(QAction("Шрифт", self, triggered=lambda: self.all_fonts.showPopup()))

        self.all_fonts.move(320, 3)
        self.size_font = QComboBox(self)
        self.size_font.addItems([str(s) for s in range(8, 32, 2)])
        self.size_font.currentIndexChanged.connect(self.change_font_size)
        self.size_font.move(200, -4)

        formatter.addAction(QAction("Размер", self, triggered=lambda: self.size_combo.showPopup()))

        menubar.addMenu(formatter)

        enter_menu = QMenu("Вставка", menubar)
        enter_menu.addAction(QAction("Вставить изображение", self, triggered=self.enter_image))
        enter_menu.addAction(QAction("Вставить ссылку", self, triggered=self.enter_link))
        menubar.addMenu(enter_menu)
        self.setMenuBar(menubar)


    def new_file(self):
        if QMessageBox.question(self, "Новый файл", "Создать новый файл?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.text_fied.clear()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)")
        if path:
            try:
                with open(path, "r") as file:
                    self.text_fied.setText(file.read())
            except FileNotFoundError:
                QMessageBox.warning(self, "Ошибка", f"Файл не найден: {path}")

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Текстовые файлы (*.txt);;Все файлы (*)")
        if path:
            try:
                with open(path, "w") as file:
                    file.write(self.text_fied.toPlainText())
            except FileNotFoundError:
                QMessageBox.warning(self, "Ошибка", f"Файл не найден: {path}")

    def change_pages(self):
        self.pages = [[" " for _ in range(self.lines)]
                      for _ in range(10)]
        self.page_number = 1

    def change_page_num(self):
        current_line = int(self.text_fied.verticalScrollBar().value() * self.lines / self.text_fied.height())
        self.current_line = current_line

        page_number = current_line // self.lines + 1
        self.page_label.setText(f"Страница {page_number}")


    '''def change_font(self, font_family):
        font = QFont(font_family, self.size_combo.currentText())
        self.text_area.setFont(font)'''


    # форматирование текста
    def change_font(self, font):
        self.apply_font(font.family())

    def apply_font(self, font_name):
        cursor = self.text_fied.textCursor()
        if cursor.hasSelection():
            char_format = cursor.charFormat()
            char_format.setFont(QFont(font_name))
            cursor.mergeCharFormat(char_format)
        else:
            self.text_fied.setFont(QFont(font_name))

    def change_font_size(self, size_index):
        font = QFont(self.all_fonts.currentFont().family(), int(self.size_combo.itemText(size_index)))
        self.text_fied.setFont(font)

    def to_bold(self):
        self.text_fied.setFontWeight(QFont.Bold)

    def to_italic(self):
        self.text_fied.setFontItalic(True)

    def to_underline(self):
        self.text_fied.setFontUnderline(True)


    # вставка картинок и ссылок
    def enter_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Вставить изображение", "", "Изображения (*.png *.jpg *.jpeg);;Все файлы (*)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.text_fied.insertHtml(f'<img src="{file_path}" width="{pixmap.width()}" height="{pixmap.height()}">')

    def enter_link(self):
        url, ok = QInputDialog.getText(self, "Вставить ссылку", "Введите URL:")
        if ok and url:  # Добавлено условие проверки на пустоту URL
            try:
                self.text_fied.insertHtml(f'<a href="{url}">{url}</a>')  # Вставка HTML ссылки
                self.text_fied.mousePressEvent(webbrowser.open(url))

                    #anchorClicked(webbrowser.open(url))
            except Exception as e:
                pass

    def open_link(self, url):
        self.web_view.load(QUrl(url.toString()))
        self.web_view.show()
        self.web_view.raise_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Processor()
    window.show()
    sys.exit(app.exec_())