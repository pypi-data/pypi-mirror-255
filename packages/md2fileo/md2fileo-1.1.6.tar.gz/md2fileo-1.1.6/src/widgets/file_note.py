from loguru import logger
from datetime import datetime

from PyQt6.QtCore  import Qt, QUrl, pyqtSlot, QSize
from PyQt6.QtGui import QDesktopServices, QResizeEvent
from PyQt6.QtWidgets import QWidget

from ..core import app_globals as ag
from .ui_file_note import Ui_fileNote
from src import tug

MIN_HEIGHT = 50
TIME_FORMAT = "%Y-%m-%d %H:%M"


class fileNote(QWidget):

    def __init__(self,
                 note_file_id: int = 0,  # file_id from filenotes table, find by hash
                 note_id: int=0,
                 modified: int=0,
                 created: int=0,
                 file_id: int=0,         # current file_id in file_list
                 parent: QWidget=None) -> None:
        super().__init__(parent)

        self.file_id = file_id if file_id else note_file_id
        self.id = note_id
        self.note_file_id = note_file_id
        self.collapsed = False

        self.modified = datetime.fromtimestamp(modified)
        self.created = datetime.fromtimestamp(created)
        self.text = ''

        self.visible_height = MIN_HEIGHT
        self.expanded_height = 0

        self.ui = Ui_fileNote()

        self.ui.setupUi(self)
        self.ui.edit.setIcon(tug.get_icon("toEdit"))
        self.ui.remove.setIcon(tug.get_icon("cancel2"))
        self.ui.created.setText(f'created: {self.created.strftime(TIME_FORMAT)}')
        self.ui.modified.setText(f'modified: {self.modified.strftime(TIME_FORMAT)}')
        self.ui.textBrowser.setOpenLinks(False)
        self.ui.textBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.ui.collapse.clicked.connect(self.toggle_collapse)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)
        self.ui.textBrowser.anchorClicked.connect(self.ref_clicked)

        self.set_collapse_icon(False)

    def set_text(self, note: str):
        self.text = note
        for pp in note.split('\n'):
            if pp:
                txt = pp
                break
        else:
            return
        self.ui.title.setText(txt[:40])

    def set_browser_text(self):
        self.ui.textBrowser.setMarkdown(self.text)
        self.set_height_by_text()
        self.updateGeometry()

    def set_height_by_text(self):
        self.ui.textBrowser.document().setTextWidth(self.ui.textBrowser.width())
        size = self.ui.textBrowser.document().size().toSize()
        self.visible_height = size.height() + self.ui.item_header.height()

    def get_note_id(self) -> int:
        return self.id

    def set_file_id(self, file_id: int):
        self.file_id = file_id

    def get_file_id(self) -> int:
        return self.file_id

    def get_note_file_id(self) -> int:
        return self.note_file_id

    def sizeHint(self) -> QSize:
        return QSize(0, self.visible_height)

    @pyqtSlot()
    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        self.collapse_item()

    def collapse_item(self):
        if self.collapsed:
            self.expanded_height = self.visible_height
            self.visible_height = self.ui.item_header.height()
            self.ui.textBrowser.hide()
        else:
            self.visible_height = self.expanded_height
            self.expanded_height = 0
            self.ui.textBrowser.show()
        self.set_collapse_icon(self.collapsed)

    @pyqtSlot()
    def check_collapse_button(self):
        if self.collapsed:
            return
        self.collapsed = True
        self.collapse_item()

    def set_collapse_icon(self, collapse: bool):
        self.ui.collapse.setIcon(
            tug.get_icon("right") if collapse
            else tug.get_icon("down")
        )

    @pyqtSlot()
    def edit_note(self):
        ag.signals_.start_edit_note.emit(self)

    @pyqtSlot()
    def remove_note(self):
        ag.signals_.delete_note.emit(self)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        scheme = href.scheme()
        if scheme == 'fileid':
            ag.signals_.user_signal.emit(f'show file\\{href.fileName()}')
        elif scheme.startswith('http') or scheme == 'file':
            QDesktopServices.openUrl(href)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if not self.collapsed:
            self.set_browser_text()
        return super().resizeEvent(a0)
