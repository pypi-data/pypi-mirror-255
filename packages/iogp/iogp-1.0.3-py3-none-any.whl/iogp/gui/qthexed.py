"""
iogp.gui.qthexed: Pure-Python PySide 6 / Qt5 hex viewer / editor.

Minimal example:

    # import random
    import sys
    # data = bytes(random.randint(0, 255) for i in range(1024))
    fn = sys.argv[-1]   # filename given as parameter or the script itself
    data = open(fn, 'rb').read()
    app = QtWidgets.QApplication()
    he = VHexEditor(data=data)
    he.show()
    sys.exit(app.exec_())

Author: Vlad Topan (vtopan/gmail)
"""
from .qt import (QWidget, Qt, SIGNAL, QScrollBar, QHBoxLayout, QVBoxLayout, QLabel,
        QShortcut, QStatusBar, QTableView, QHeaderView, QPlainTextEdit, QFont, QFontMetrics,
        QStandardItemModel, QColor, QBrush, QStandardItem, QTextOption, QTextCursor,
        QTextCharFormat, QRect, QItemSelection, QItemSelectionModel)
from ..data import DataView, CP437_TO_UNICODE, decode_cp437, AttrDict


NONPRINTABLE = {k: CP437_TO_UNICODE[k] for k in (0, 7, 8, 9, 10, 13, 0x7F)}

STYLE = AttrDict({
    'even_text': '#800',
    'odd_text': '#008',
    'selection': '#66F',
    'background': '#FFF',
    'highlight': '#DD6',
    'font': 'Terminal',
    'font_size': 8,
})

# todo: more flexible styling
HEADER_CSS = '''
::section {
    border: 0px;
    padding: 1px;
    text-align: center;
    font: monospace;
    }
::section:checked {
    color: white;
    font-weight: normal;
    background-color: blue;
    }
::section:hover {
    color: blue;
    }
'''

TABLE_CSS = '''
::item {
    gridline-color: white;
    }
::item:focus {
    border: 0px;
    color: red;
    gridline-color: white;
    }
::item:hover {
    color: blue;
    }
'''

BINVIEW_CSS = '''
'''



class VBaseEditor(QWidget):
    """
    Base class for VHexEditor and VBinViewer.
    """
    def __init__(self, viewer, data=None, filename=None, readonly=True, statusbar=1, columns=16,
                min_width=800, style=None):
        super().__init__()
        self.viewer = viewer
        self.set_style(style)
        self._font = QFont(self.style.font, self.style.font_size)
        self.metrics = QFontMetrics(self._font)
        self.row_height = self.metrics.height() + 4
        if columns is None:
            columns = 80
        self.columns = columns
        self.rows = 1
        self.perpage = self.columns * self.rows
        self.scroll = QScrollBar(Qt.Vertical)
        self.scroll.setPageStep(1)
        self.scroll.valueChanged[int].connect(self.jump_to_row)
        self.l1 = QVBoxLayout()
        self.l2 = QHBoxLayout()
        self.l2.addWidget(self.viewer)
        self.l2.addWidget(self.scroll)
        self.l1.addLayout(self.l2)
        self.statusbar = statusbar and QStatusBar()
        if self.statusbar:
            self.l1.addWidget(self.statusbar)
            self.status = {}
            self.status['filename'] = QLabel('-')
            self.lbl_offset = QLabel('Offset:')
            self.status['offset'] = QLabel('-')
            self.statusbar.addWidget(self.status['filename'])
            self.statusbar.addWidget(self.lbl_offset)
            self.statusbar.addWidget(self.status['offset'])
        self.setLayout(self.l1)
        self.setMinimumWidth(min_width)
        self.dv = None
        self.own_dv = False
        self.open(data, filename, readonly)

    def set_style(self, style):
        """
        Set styling dict (see `STYLE` for keys).
        """
        self.style = AttrDict(STYLE)
        if style:
            # todo: use .style in currently-hardcoded locations
            self.style.update(style)

    def wheelEvent(self, evt):
        """
        Hooked to implement scrolling by mouse wheel.
        """
        self.jump_rows(1 if evt.angleDelta().y() > 0 else -1)
        evt.accept()

    def keyPressEvent(self, evt):
        """
        Hooked to implement scrolling by up/down/pgup/pgdn.

        Note: only events which aren't caught by self.viewer end up here.
        """
        key = evt.key()
        if key in (Qt.Key_PageUp, Qt.Key_PageDown):
            self.jump_pages(1 if key == Qt.Key_PageUp else -1)
            evt.accept()
        elif key in (Qt.Key_Up, Qt.Key_Down):
            self.jump_rows(1 if key == Qt.Key_Up else -1)
            evt.accept()

    def open(self, data=None, filename=None, readonly=True):
        """
        Open a file (or a data buffer).
        """
        self.offs = 0
        if self.dv is not None and self.own_dv:
            self.dv.close()
        if isinstance(data, DataView):
            self.dv = data
            self.own_dv = False
        else:
            self.dv = DataView(data=data, filename=filename, readonly=readonly)
            self.own_dv = True
        self.size = len(self.dv)
        self.scroll.setRange(0, self.size // self.columns)
        if self.statusbar:
            self.status['filename'].setText((f'File: <b>{filename}</b>')
                    if filename else (f'Raw data ({self.size} bytes)'))
        self.update()

    def jump_pages(self, pages=1):
        """
        Jump a number of pages up / down.

        :param pages: Number of pages to jump; negative values jump down.
        """
        self.jump(self.offs - pages * self.perpage)

    def jump_rows(self, rows=1):
        """
        Jump a number of rows up / down.

        :param rows: Number of rows to jump; negative values jump down.
        """
        self.jump(self.offs - rows * self.columns)

    def jump_to_row(self, row):
        """
        Jump to the given row id.
        """
        self.jump(row * self.columns)

    def update(self):
        """
        Update contents.
        """
        self.jump(force=True)



class VBinViewer(VBaseEditor):
    """
    Binary viewer widget.

    :param data: The raw data (bytes or bytearray).
    :param filename: The file name containing the data.
    :param columns: Number of columns (default: fit window).
    """

    def __init__(self, data=None, filename=None, statusbar=1, columns=None, min_width=800,
                style=None):
        super().__init__(QPlainTextEdit(),
                data=data, filename=filename, readonly=True, statusbar=statusbar,
                columns=columns, min_width=min_width, style=style)
        self.viewer.setWordWrapMode(QTextOption.WrapAnywhere)
        self.viewer.setFont(self._font)
        self.update()

    def sel_changed(self, new, old):
        """
        Selection changing is monitored to allow highlighting matching selected bytes between the
        hex dump and the text.
        """

    def jump(self, offs=0, force=False):
        """
        Jump to an offset.
        """
        new_offs = min(max(0, offs), max(0, len(self.dv) - self.perpage))
        new_offs = new_offs // self.columns * self.columns
        # print('JUMP:', new_offs, self.offs, force)
        if (new_offs != self.offs) or force:
            self.offs = new_offs
            decoded = decode_cp437(self.current_data)
            decoded = '\n'.join(decoded[i:i + self.columns] for i in range(0, len(decoded),
                    self.columns))
            self.viewer.setPlainText(decoded)

    def resizeEvent(self, evt):
        """
        This keeps self.rows/columns/perpage updated and regenerates the self.viewer content.
        """
        rect = self.viewer.fontMetrics().boundingRect('W')
        self.rows = (self.viewer.height() - 10) // rect.height()
        self.columns = (self.viewer.width() - 30) // rect.width()
        self.perpage = self.columns * self.rows
        self.scroll.setRange(0, self.size // self.columns)
        self.update()
        super().resizeEvent(evt)

    def adjust_pos_from_gui(self, pos):
        """
        Compute file offset from GUI / selection offset (subtract newlines, add offs).
        """
        res = pos - pos // self.columns + self.offs
        return res

    def adjust_pos_to_gui(self, pos):
        """
        Compute GUI offset from file offset (add newlines, subtract offs).
        """
        res = pos - self.offs
        res += res // self.columns
        return res

    @property
    def current_data(self):
        """
        The currently-displayed data.
        """
        return self.dv[self.offs:self.offs + self.perpage]

    @property
    def sel_start(self):
        """
        Selection start.
        """
        pos = self.viewer.textCursor().selectionStart()
        print('SELSTART:', pos)
        if pos is not None:
            pos = self.adjust_pos_from_gui(pos)
        return pos

    @property
    def sel_end(self):
        """
        Selection end.
        """
        pos = self.viewer.textCursor().selectionEnd()
        if pos is not None:
            pos = self.adjust_pos_from_gui(pos)
        return pos

    @property
    def sel_length(self):
        """
        Selection length.
        """
        tc = self.viewer.textCursor()
        return tc.selectionEnd() - tc.selectionStart()

    def select(self, start, end, jump=True):
        """
        Select text by offset.
        """
        if jump:
            self.jump(max(0, start - 2 * self.columns))
        start = self.adjust_pos_to_gui(start)
        end = self.adjust_pos_to_gui(end)
        cur = self.viewer.textCursor()
        # print('moving selection: setpos:', start)
        cur.setPosition(start)
        cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, n=end - start)
        self.viewer.setTextCursor(cur)

    def highlight(self, ranges):
        """
        Highlight a list of (start, end) ranges.
        """
        cursor = QTextCursor(self.document())
        for start, end in ranges:
            # keep track of newlines
            cursor.setPosition(start + start // self.columns)
            cursor.setPosition(end + end // self.columns, QTextCursor.KeepAnchor)
            format = QTextCharFormat()
            format.setBackground(QColor(self.style.highlight))
            cursor.mergeCharFormat(format)

    def __getattr__(self, attr):
        """
        Forward some methods.
        """
        if attr in ('document',):
            return getattr(self.viewer, attr)
        raise AttributeError(f'Invalid attribute: {attr}!')



class VHexEditor(VBaseEditor):
    """
    Hex editor widget.

    :param data: The raw data (bytes or bytearray).
    :param filename: The file name containing the data.
    """

    def __init__(self, data=None, filename=None, readonly=True, statusbar=1, columns=16,
                min_width=800, style=None):
        super().__init__(QTableView(showGrid=0, styleSheet=TABLE_CSS),
                data=data, filename=filename, readonly=readonly, statusbar=statusbar,
                columns=16, min_width=min_width, style=style)
        self.viewer.setFont(self._font)
        self.dm = QStandardItemModel(self.rows, self.columns)
        self.viewer.setModel(self.dm)
        self.viewer.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.viewer.horizontalHeader().setHighlightSections(1)
        self.viewer.verticalHeader().setHighlightSections(1)
        self.viewer.horizontalHeader().setStretchLastSection(0)
        self.viewer.selectionModel().selectionChanged.connect(self.sel_changed)
        self.update()

    def sel_changed(self, new, old):
        """
        Selection changing is monitored to allow highlighting matching selected bytes between the
        hex dump and the text.
        """
        new, old = ([(e.row(),
                (e.column() + self.columns) % (2 * self.columns))
                for e in lst.indexes()] for lst in (new, old))
        for e in old:
            if e in new:
                continue
            if item := self.dm.item(*e):
                item.setBackground(QColor(self.style.background))
        for e in new:
            if e in old:
                continue
            if item := self.dm.item(*e):
                item.setBackground(QColor(self.style.selection))
        if self.statusbar:
            idx = self.viewer.selectionModel().currentIndex()
            offs = self.offs + idx.row() * self.columns + idx.column()
            self.status['offset'].setText('<b>0x%X</b> (%d)' % (offs, offs))

    def select(self, start, count, jump=True):
        """
        Select a range of bytes.
        """
        base_row = max(0, (start // self.columns) - 1)
        if jump:
            self.jump_to_row(base_row)
        base_row = self.offs // self.columns
        selmdl = self.viewer.selectionModel()
        mdl = self.viewer.model()
        selmdl.clearSelection()
        max_rows = self.rows
        # todo: use QTextCursor.NextCell?
        while count > 0 and max_rows >= 0:
            row = start // self.columns - base_row
            col1 = start % self.columns
            col2 = min(self.columns - 1, col1 + count - 1)
            selected = col2 - col1 + 1
            count -= selected
            start += selected
            # todo: use row selection when support is added
            #if selected == self.columns:
            #    selmdl.select(mdl.index(row, 0), QItemSelectionModel.Select | QItemSelectionModel.Rows)
            #else:
            selmdl.select(QItemSelection(mdl.index(row, col1), mdl.index(row, col2)), QItemSelectionModel.Select)
            max_rows -= 1

    def resizeEvent(self, evt):
        """
        This keeps self.rows/columns/perpage updated and regenerates the self.viewer content.
        """
        self.rows = (self.viewer.height()
                - self.viewer.verticalHeader().height() - 6) // self.row_height
        self.perpage = self.columns * self.rows
        self.dm.setRowCount(self.rows)
        self.scroll.setRange(0, self.size // self.columns)
        self.jump(self.offs)
        super().resizeEvent(evt)

    @property
    def sel_start(self):
        """
        Selection start.
        """
        idx = self.viewer.selectionModel().currentIndex()
        if col := self.column() >= self.columns + 1:
            col -= self.columns + 1
        else:
            col -= 1
        return idx.row() * self.columns + max(0, col)

    @property
    def sel_end(self):
        """
        Selection end.
        """
        idx = self.viewer.selectionModel().selectedIndexes()[-1]
        if col := self.column() >= self.columns + 1:
            col -= self.columns + 1
        else:
            col -= 1
        return idx.row() * self.columns + max(0, col)

    def jump(self, offs=0, force=False):
        """
        Jump to the given offset (this is the main workhorse which updates self.viewer contents).
        """
        # todo: only update on `force` or of offs != self.offs
        brushes = [QBrush(QColor(x)) for x in (self.style.odd_text, self.style.even_text)]
        hv = self.viewer
        if not hv.selectionModel():
            return
        crt = hv.selectionModel().currentIndex()
        vh = hv.verticalHeader()
        hh = hv.horizontalHeader()
        # ## get data window
        self.offs = max(0, min(offs, self.size - self.perpage))
        data = self.dv[self.offs:self.offs + self.perpage]
        # ## generate & set labels
        addrlabels = ['%08X' % i for i in range(self.offs, self.offs + self.perpage, self.columns)]
        self.dm.setVerticalHeaderLabels(addrlabels)
        self.dm.setHorizontalHeaderLabels([str(x) for x in range(self.columns)]
                + [''] * self.columns)
        # ## generate data for datamodel (actual viewer contents)
        idx = 0   # offset inside the data window (index in `data`)
        for row in range(self.rows):
            for col in range(self.columns):
                if idx < len(data):
                    c = data[idx]
                    hitem = QStandardItem('%02X' % c)
                    hitem.setTextAlignment(Qt.AlignCenter)
                    hitem.setForeground(brushes[col % 2])
                    titem = QStandardItem(bytes([
                            32 if c in NONPRINTABLE else c]).decode('cp437'))
                    titem.setTextAlignment(Qt.AlignCenter)
                    titem.setForeground(brushes[col % 2])
                else:
                    hitem = titem = None
                self.dm.setItem(row, col, hitem)
                self.dm.setItem(row, col + self.columns, titem)
                idx += 1
        # ## format view
        hh.setDefaultSectionSize(hv.fontMetrics().horizontalAdvance('A') + 2)
        hh.setMaximumSectionSize(hv.fontMetrics().horizontalAdvance('AAA'))
        for i in range(self.columns):
            hh.resizeSection(i, hv.fontMetrics().horizontalAdvance('A') + 2)
        vh.setDefaultSectionSize(self.row_height)
        vh.setDefaultAlignment(Qt.AlignCenter)
        vh.setStyleSheet(HEADER_CSS)
        hh.setStyleSheet(HEADER_CSS)
        # ## restore pre-scroll selection
        hv.setCurrentIndex(crt)
