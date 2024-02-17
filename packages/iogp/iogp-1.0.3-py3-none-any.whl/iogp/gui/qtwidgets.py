"""
iogp.gui.qtwidgets: Custom Qt widgets.

Author: Vlad Topan (vtopan/gmail)
"""
import html
import threading
import time

from .qt import (QTextBrowser, QFontMetrics, QLineEdit, QTextEdit, QHBoxLayout, QLabel, QComboBox)
from .qthexed import VHexEditor, VBinViewer



class VMessageLog(QTextBrowser):

    def __init__(self, *args, rows=4, hint='Log messages', log_timestamps=False,
                open_external_links=True, **kwargs):
        # todo: more flexible style control
        super().__init__(*args, **kwargs)
        self.setStyleSheet('QScrollBar:vertical {width: 10px;}')
        self.setPlaceholderText(hint)
        self.setReadOnly(1)
        if rows:
            rowheight = QFontMetrics(self.font()).lineSpacing()
            self.setFixedHeight(10 + rows * rowheight)
        self.setOpenExternalLinks(open_external_links)
        self.lock = threading.Lock()
        self.log_timestamps = log_timestamps

    def log(self, msg, escape=True):
        """
        Log a message.
        """
        self.lock.acquire()
        if escape:
            msg = html.escape(msg)
        if msg.startswith('[DEBUG]'):
            msg = f'<font color="#444">{msg}</font>'
        elif msg.startswith('[ERROR]') or msg.startswith('[CRASH]'):
            msg = f'<font color="#A00">{msg}</font>'
        if self.log_timestamps:
            msg = f'<font color="#777">{time.strftime("[%d.%m.%y %H:%M:%S]")}</font> {msg}'
        if escape:
            msg = msg.replace('\n', '<br>')
        self.append(msg)
        self.ensureCursorVisible()
        self.lock.release()



def VLabelEdit(label, value='', placeholder='', validator=None, cls=QLineEdit, hint=None):
    """
    Returns a horizontal layout containing a label and an edit.

    The label and layout widgets are accessible as the `.label` / `.layout` attributes of the
    edit widget.
    """
    obj = cls()
    obj.label = QLabel(label)
    lay = obj.parent_layout = QHBoxLayout()
    lay.addWidget(obj.label)
    lay.addWidget(obj)
    obj.label.setBuddy(obj)
    if validator:
        obj.setValidator(validator)
    if isinstance(obj, QLineEdit):
        lay.text = obj.text
        lay.setText = obj.setText
    elif isinstance(obj, QTextEdit):
        lay.text = obj.toPlainText
        lay.setText = obj.setPlainText
    elif isinstance(obj, QComboBox):
        lay.text = obj.currentText
        lay.setText = obj.setCurrentText
    if value:
        lay.setText(value)
    if hint:
        obj.label.setToolTip(hint)
        obj.setToolTip(hint)
    if placeholder:
        obj.setPlaceholderText(placeholder)
    return obj
