"""
iogp.gui.qt: GUI wrappers and helper functions for PySide6 (Qt5).

Author: Vlad Topan (vtopan/gmail)
"""
import fnmatch
from logging import error, warn, info
import re

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import (SIGNAL, QByteArray, QCoreApplication, QDate, QDateTime,  # noqa: F401
        QEvent, QSortFilterProxyModel, Qt, QThread, Signal, Slot, QRect, QItemSelection,
        QItemSelectionModel)
from PySide6.QtGui import (QBrush, QClipboard, QColor, QCursor, QDesktopServices,  # noqa: F401
        QFont, QFontMetrics, QIcon, QIntValidator, QKeySequence, QPalette, QPixmap, QShortcut,
        QStandardItem, QStandardItemModel, QTextCursor, QTextOption, QAction, QTextCharFormat)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,  # noqa: F401
        QCompleter, QDateEdit, QDateTimeEdit, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
        QHeaderView, QLabel, QLayout, QLineEdit, QListWidget, QMainWindow, QMessageBox,
        QPlainTextEdit, QPushButton, QScrollBar, QStatusBar, QStyleFactory, QTableView,
        QTableWidget, QTableWidgetItem, QTabWidget, QTextBrowser, QTextEdit, QTreeWidget,
        QTreeWidgetItem, QBoxLayout, QVBoxLayout, QWidget, QMenu, QMenuBar)

from ..data import AttrDict



class WidgetManager:
    """
    Widget manager for PySide6/Qt5.
    """

    def __init__(self, parent, widgets=None, auto_save_fields=None):
        self.widgets = None
        self.parent = parent
        self.auto_save_fields = auto_save_fields
        if widgets:
            self.load_widgets(widgets)

    def load_widgets(self, widgets):
        """
        Converts recursive structures of lists, dicts and GUI widgets to a proper PySide6 layout.

        A list is converted to a QVBoxLayout, a dict to a QHBoxLayout, everything else is presumed
        to be a widget and simply added to the current layout. The keys in each dict are mapped to
        the corresponding widgets in the output `.widgets` dict.

        Known keywords:
        - '!tab' converts a dict to a QTabWidget
        - '!vertical' converts a dict to a QVBoxLayout instead of a QHBoxLayout
        - '!horizontal' converts a list to a QHBoxLayout instead of a QVBoxLayout
        - '!border' creates a border (QFrame) around the layout (the value can be CSS styling)
        - '!stretch' sets stretching rules (e.g. '!stretch': (0, 2) sets the stretch property of
            widget 0 to 2; can be a list of tuples to set the stretch for multiple widgets

        :return: The top-level layout.
        """
        self.layout = None
        self.widgets = {}
        self.tabs = []
        if isinstance(widgets, str):
            # todo parse as JSON
            raise NotImplementedError(':(')
        if isinstance(widgets, (dict, list)):
            self.layout = self.create_layouts(widgets)
        else:
            raise ValueError(
                    f'Cannot process {widgets} of type {type(widgets)}, should be dict or JSON str!'
            )

    def create_layouts(self, widgets, name=None):
        """
        Parse the nested widget structure and generate the layout tree.
        """

        def _handle_directive(name, value=None):
            nonlocal layout
            if name.startswith('!stretch'):
                if not isinstance(value, list):
                    value = [value]
                for e in value:
                    layout.setStretch(*e)
            elif name == '!border':
                panel.setFrameStyle(QFrame.StyledPanel)
                panel.setStyleSheet('QFrame { margin: 0px; border: 1px solid #888; padding: 1px; }')
            elif name.startswith('!max_'):
                what = name.split('_')[1].title()
                if what not in ('Width', 'Height', 'Size'):
                    raise ValueError(f'Unknown directive {name}!')
                getattr(panel, 'setMaximum' + what)(value)
            elif name in ('!horizontal', '!vertical', '!tab', '!panel'):
                pass
            else:
                raise ValueError(f'Unknown directive {name}!')

        if not isinstance(widgets, (list, dict)):
            raise ValueError('The toplevel node must be a list or a dict!')
        if '!' in widgets:
            # a single '!' key can hold a sequence of directives
            widgets.update({e: ... for e in widgets.pop('!')})
        panel = None
        if '!panel' in widgets or '!max_width' in widgets or '!border' in widgets:
            panel = QFrame()
            panel.setStyleSheet('QFrame { margin: 0px; border: 0px; padding: 0px; }')
        layout = QVBoxLayout() if ((isinstance(widgets, list) and '!horizontal' not in widgets)
                or '!vertical' in widgets) else QHBoxLayout()
        tab = None
        if '!tab' in widgets:
            tab = QTabWidget()
            self.tabs.append(tab)
            self.widgets[name] = tab
            layout.addWidget(tab)
        if tab and not isinstance(widgets, dict):
            raise ValueError('Tab widgets must be dicts!')
        wsettings = {}
        for widget in widgets:
            if widget == '!tab':
                continue
            w_name = None
            add_layout_fun = layout.addLayout
            if isinstance(widgets, dict):
                w_name, widget = widget, widgets[widget]
            # handle directives
            if isinstance(w_name, str) and w_name[0] == '!':
                _handle_directive(w_name, widget)
                continue
            elif isinstance(widget, str):
                _handle_directive(widget)
                continue
            # add this widget(s) or layout
            if tab:
                tab_widget = QWidget()
                tab.addTab(tab_widget, w_name)
                add_layout_fun = tab_widget.setLayout
            if isinstance(widget, (list, dict)):
                widget = self.create_layouts(widget, name=w_name)
                add_layout_fun(widget)
            elif isinstance(widget, QLayout):
                add_layout_fun(widget)
            elif hasattr(widget, 'parent_layout'):   # VLabelEdit
                add_layout_fun(widget.parent_layout)
            else:
                if tab:
                    tab_layout = QVBoxLayout()
                    tab_widget.setLayout(tab_layout)
                    tab_layout.addWidget(widget)
                else:
                    layout.addWidget(widget)
                for k, v in wsettings.items():
                    getattr(widget, k)(v)
            prev = self.widgets.get(w_name, None)
            if (not prev) or isinstance(prev, (QHBoxLayout, QVBoxLayout, QGridLayout)):
                self.widgets[w_name] = widget
                widget.setObjectName(w_name)
        if panel:
            panel.setLayout(layout)
            layout = QHBoxLayout()
            layout.addWidget(panel)
        return layout

    def connect_events(self):
        """
        Connect self.parent.<btn_widget_name>_clicked handlers to .clicked events and others.
        """
        for k, v in self.widgets.items():
            for cls, signal, suffix, warn_if_missing in [
                    (QPushButton, 'clicked', 'clicked', True),
                    (QLineEdit, 'returnPressed', 'pressed_enter', False),
                    (QComboBox, 'currentTextChanged', 'changed', False),
                    (QCheckBox, 'stateChanged', 'changed', False),
                    ]:
                if isinstance(v, cls):
                    name = k + '_' + suffix
                    method = getattr(self.parent, name, None)
                    if method:
                        getattr(self[k], signal).connect(method)
                    elif warn_if_missing:
                        warn(f'Missing .{name}()!')

    def save_to_cfg(self, cfg, fields=None, keys=('history', 'field_values')):
        """
        Auto-save GUI field values to the given subkey of cfg.
        """
        fields = fields or self.auto_save_fields or []
        for k in keys:
            if k not in cfg:
                cfg[k] = AttrDict()
            cfg = cfg[k]
        for field in fields:
            lst = fnmatch.filter(self.wmap, field) if '*' in field else [field]
            for k in lst:
                widget = self[k]
                for (wtype, meth) in [
                        (QCheckBox, 'isChecked'),
                        (QComboBox, 'currentText'),
                        (QListWidget, lambda x: [x.item(i).text() for i in range(x.count())]),
                        (QTextBrowser, 'toHtml'),
                        ]:
                    if isinstance(widget, wtype):
                        val = getattr(widget, meth)() if isinstance(meth, str) else meth(widget)
                        break
                else:
                    val = widget.text()
                cfg[k] = val

    def load_from_cfg(self, cfg, keys=('history', 'field_values')):
        """
        Load widget contents from the given subkeys of cfg.
        """
        for k in keys:
            if k not in cfg:
                cfg[k] = AttrDict()
            cfg = cfg[k]
        for k, v in list(cfg.items()):
            if v:
                if not hasattr(self, k):
                    del cfg[k]
                    continue
                widget = self[k]
                for (wtype, meth) in [
                        (QCheckBox, 'setChecked'),
                        (QComboBox, 'setCurrentText'),
                        (QListWidget, 'addItems'),
                        (QTextBrowser, 'setHtml'),
                        ]:
                    if isinstance(widget, wtype):
                        getattr(widget, meth)(v)
                        break
                else:
                    widget.setText(v)

    def __getattr__(self, name):
        if name in self.widgets:
            return self.widgets[name]
        super().__getattribute__(name)

    def __contains__(self, name):
        return name in self.widgets

    def __getitem__(self, name):
        return self.widgets[name]



def apply_style(style, cfg, main_window, wm=None, additional_colors=None, custom_css=None):
    """
    Apply a style from cfg.path('stylesheets')
    """
    if wm is None:
        wm = main_window.wm
    cfg.style.colors = colors = AttrDict(Background='#F8F8F0', Text='#111111', Grid='#BBBBBB',
            Line='#111111', link='initial')
    if style == 'Default':
        css = ''
    else:
        try:
            filename = f'{cfg.path("stylesheets")}/{style}.style'
            info(f'Loading style from {filename}...')
            for line in open(filename):
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                k, v = re.search(r'(^[^:]+):\s+(.+)$', line).groups()
                colors[k] = v
        except Exception as e:
            return error(f'Failed loading style from {filename}: <{e.__class__.__name__}> {e}')
        css_tree = {
            'QCheckBox::indicator': ['  border: 1px solid;'],
            'QLineEdit': ['  border: 1px solid;', '  padding: 0px;'],
            'QTabBar::tab': ['  border-width: 1px;', '  border-style: solid;',
                    '  padding: 2px 5px 2px 5px;', '  border-radius: 3px;', '  margin: 2px;'],
            'QToolTip': ['  border: 0;'],   # without this, the background color is not applied...
            'QTableWidget': ['  outline: 0;'],
            'QTableWidget::item': ['  border: 1px solid;'],
            'QTableWidget::selected': ['  border: 1px solid;'],
            # 'QPushButton': ['  border-radius: 3px;']
            }
        # todo: better styling, get non-color options from .style - ref https://doc.qt.io/qt-6/stylesheet-examples.html
        for field, maps_to in {
                'background': {
                    'background-color': ['*', 'QTabBar::tab', 'QCheckBox::indicator:unchecked',
                            'QHeaderView::section',     # for table (QTableWidget) headings
                        ],
                    'color': ['QCheckBox::indicator:checked'],
                    },
                'editable': {
                    'background-color': ['QLineEdit', 'QListWidget', 'QComboBox'],
                    },
                'text': {
                    'color': ['*'],
                    },
                'selection': {
                    'background-color': ['QTabBar::tab:selected', 'QListView::item:selected',
                            'QTableWidget::item:selected'
                        ],
                    },
                'lines': {
                    'border-color': ['*', 'QCheckBox::indicator', 'QLineEdit', 'QListWidget',
                            'QTabBar::tab', 'QTabWidget', 'QCheckBox'
                        ],
                    },
                'hover': {
                    'background-color': [
                            'QToolTip',
                            'QCheckBox::indicator:indeterminate:hover',
                            'QCheckBox::indicator:pressed',
                            'QCheckBox::indicator:checked:hover',
                            'QCheckBox::indicator:unchecked:hover',
                            'QCheckBox::indicator:indeterminate:hover',
                            'QPushButton:hover', 'QLineEdit:hover', 'QTabBar:hover', 'QListView::item:hover',
                            'QTableWidget::item:hover',
                        ],
                    },
                'buttons': {
                    'background-color': ['QPushButton', 'QCheckBox:indicator'],
                    },
                'checkbox_image': {
                    'image': ['QCheckBox::indicator:checked'],
                    }
                }.items():
            if field not in colors:
                continue
            for name, cats in maps_to.items():
                for cat in cats:
                    if cat not in css_tree:
                        css_tree[cat] = []
                    css_tree[cat].append(f'  {name}: {colors[field]};')
        css = []
        for cat, values in sorted(css_tree.items()):
            css += [f'{cat} {{'] + sorted(values) + ['}\n']
        css = '\n'.join(css).replace('$img', cfg.path('images'))
    if custom_css:
        css += '\n\n' + custom_css
    open(f'{cfg.path("stylesheets")}/current.css', 'w').write(css)
    main_window.setStyleSheet(css)


# monkey-patch sensible methods for layouts
def add_to_layout(self, *things, **kwargs):
    for thing in things:
        if isinstance(thing, QLayout):
            self.addLayout(thing)
        else:
            self.addWidget(thing)
    for name, thing in kwargs.items():
        if isinstance(thing, QLayout):
            self.addLayout(thing)
        else:
            self.addWidget(thing)
        setattr(self, name, thing)


QHBoxLayout.add = add_to_layout
QVBoxLayout.add = add_to_layout


def menu_from_dict(win, menu, mdict):
    """
    Creates a menu based on a dict template.

    :param win: Window (Qt object with the `menu_...()` action handlers).
    """
    if not hasattr(win, 'menus'):
        win.menus = {}
    for k, v in mdict.items():
        if k.startswith('-'):
            menu.addSeparator()
        else:
            if type(v) is dict:
                submenu = QMenu(k)
                win.menus[k] = submenu
                menu.addMenu(submenu)
                menu_from_dict(win, submenu, v)
            else:
                handler = getattr(win, 'menu_' + re.sub(r'\W+', '', k), None)
                if handler:
                    action = menu.addAction(QAction(k, win, triggered=handler, shortcut=v))
                    win.menus[k] = action
