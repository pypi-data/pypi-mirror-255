from types import FunctionType, BuiltinFunctionType, MethodType

from PyQt6.QtWidgets import QWidget,  QPushButton, QFrame, QLabel, QTreeView, QHeaderView
from PyQt6.QtWidgets import QSizePolicy, QAbstractItemView
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import QRect, Qt, QSize

from .lib import resize_tree_table

FUNC = (FunctionType, BuiltinFunctionType, MethodType)

SMINMIN = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
SMAXMAX = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
SMAXMIN = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
SMINMAX = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

ATOP = Qt.AlignmentFlag.AlignTop
ARIGHT = Qt.AlignmentFlag.AlignRight
ALEFT = Qt.AlignmentFlag.AlignLeft
ACENTER = Qt.AlignmentFlag.AlignCenter
AVCENTER = Qt.AlignmentFlag.AlignVCenter

RFIXED = QHeaderView.ResizeMode.Fixed

SMPIXEL = QAbstractItemView.ScrollMode.ScrollPerPixel

class WidgetBuilder():

    from .styles import get_style_class, get_style, merge_style, theme_font

    def __init__(self) -> None:
        """
        This class is not inteded to be instantiated.
        """
        return

    def create_button(self, text, style:str='', parent=None, style_override={}):
        """
        Creates a button according to style with parent.

        Parameters:
        - :param text: text to be shown on the button
        - :param style: name of the style as in self.theme or style dict
        - :param parent: parent of the button (optional)
        - :param style_override: style dict to override default style (optional)

        :return: configured QPushButton
        """
        button = QPushButton(text, parent)
        button.setStyleSheet(self.get_style_class('QPushButton', style, style_override))
        if 'font' in style_override:
            button.setFont(self.theme_font(style, style_override['font']))
        else:
            button.setFont(self.theme_font(style))
        button.setSizePolicy(SMAXMAX)
        return button

    def create_icon_button(self, icon, style:str='', parent=None, style_override={}):
        """
        Creates a button showing an icon according to style with parent.

        Parameters:
        - :param icon: icon to be shown on the button
        - :param style: name of the style as in self.theme or style dict
        - :param parent: parent of the button (optional)
        - :param style_override: style dict to override default style (optional)

        :return: configured QPushButton
        """
        button = QPushButton('', parent)
        button.setIcon(icon)
        button.setStyleSheet(self.get_style_class('QPushButton', style, style_override))
        icon_size = self.theme['s.c']['button_icon_size']
        button.setIconSize(QSize(icon_size, icon_size))
        button.setSizePolicy(SMAXMAX)
        return button

    def create_frame(self, parent, style='frame', style_override={}):
        """
        Creates a frame with default styling and parent

        Parameters:
        - :param parent: parent of the frame (optional)
        - :param style: style dict to override default style (optional)

        :return: configured QFrame
        """
        frame = QFrame(parent)
        frame.setStyleSheet(self.get_style(style, style_override))
        frame.setSizePolicy(SMAXMAX)
        return frame

    def create_label(self, text, style:str='', parent=None, style_override={}):
        """
        Creates a label according to style with parent.

        Parameters:
        - :param text: text to be shown on the label
        - :param style: name of the style as in self.theme
        - :param parent: parent of the label (optional)
        - :param style_override: style dict to override default style (optional)

        :return: configured QLabel
        """
        label = QLabel(parent)
        label.setText(text)
        label.setStyleSheet(self.get_style(style, style_override))
        label.setSizePolicy(SMAXMAX)
        if 'font' in style_override:
            label.setFont(self.theme_font(style, style_override['font']))
        else:
            label.setFont(self.theme_font(style))
        return label
        
    def create_button_series(self, parent, buttons:dict, style, shape:str='row', seperator:str='', ret=False):
        """
        Creates a row / column of buttons.

        Parameters:
        - :param parent: widget that will contain the buttons
        - :param buttons: dictionary containing button details
        - :param style: key for self.theme -> default style
        - :param shape: row / column
        - :param seperator: string seperator displayed between buttons (optional)

        :return: populated QVBoxlayout / QHBoxlayout
        """
        if 'default' in buttons:
            defaults = self.merge_style(self.theme[style], buttons.pop('default'))
        else:
            defaults = self.theme[style]

        if shape == 'column':
            layout = QVBoxLayout()
        else:
            shape = 'row'
            layout = QHBoxLayout()
    	
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        button_list = []
        
        if seperator != '':
            sep_style = {'color':defaults['color'],'margin':0, 'padding':0, 'background':'rgba(0,0,0,0)'}
        
        for i, (name, detail) in enumerate(buttons.items()):
            if 'style' in detail:
                button_style = self.merge_style(defaults, detail['style'])
            else:
                button_style = defaults
            bt = self.create_button(name, style, parent, button_style)
            if 'callback' in detail and isinstance(detail['callback'], FUNC):
                bt.clicked.connect(detail['callback'])
            stretch = detail['stretch'] if 'stretch' in detail else 0
            if 'align' in detail:
                layout.addWidget(bt, stretch, detail['align'])
            else:
                layout.addWidget(bt, stretch)
            button_list.append(bt)
            if seperator != '' and i < (len(buttons) - 1):
                sep_label = self.create_label(seperator, 'label', parent, sep_style)
                sep_label.setSizePolicy(SMAXMIN)
                layout.addWidget(sep_label)
        
        if ret: return layout, button_list
        else: return layout
            
    def create_analysis_table(self, parent, widget) -> QTreeView:
        """
        Creates and returns a QTreeView with parent, styled according to widget.

        Parameters:
        - :param parent: parent of the table
        - :param widget: style key for the table

        :return: configured QTreeView
        """
        table = QTreeView(parent)
        table.setStyleSheet(self.get_style_class('QTreeView', widget))
        table.setSizePolicy(SMINMIN)
        table.setAlternatingRowColors(True)
        table.setHorizontalScrollMode(SMPIXEL)
        table.setVerticalScrollMode(SMPIXEL)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)
        table.header().setStyleSheet(self.get_style_class('QHeaderView', 'tree_table_header'))
        table.header().setSectionResizeMode(RFIXED)
        #table.header().setSectionsMovable(False)
        table.header().setMinimumSectionSize(1)
        table.header().setSectionsClickable(True)
        table.header().setStretchLastSection(False)
        table.expanded.connect(lambda: resize_tree_table(table))
        table.collapsed.connect(lambda: resize_tree_table(table))
        return table

class FlipButton(QPushButton):
    """
    QPushButton with two sets of commands, texts and icons that alter on click.
    """
    def __init__(self, r_text, l_text, parent, *ar, **kw):
        super().__init__(r_text, parent, *ar, **kw)
        self._r = True
        self._r_text = r_text
        self._l_text = l_text
        self.setText(r_text)
        self._r_function = self._f
        self._l_function = self._f
        self._r_icon = None
        self._l_icon = None
        self.clicked.connect(self.flip)

    def flip(self):
        if self._r:
            self._r_function()
            self.setIcon(self._l_icon)
            self.setText(self._l_text)
            self._r = not self._r
        else:
            self._l_function()
            self.setIcon(self._r_icon)
            self.setText(self._r_text)
            self._r = not self._r

    def set_icon_r(self, icon:QIcon):
        self._r_icon = icon
        if self._r:
            self.setIcon(icon)

    def set_icon_l(self, icon:QIcon):
        self._l_icon = icon
        if not self._r:
            self.setIcon(icon)

    def set_text_r(self, text):
        self._r_text = text
        if self._r:
            self.setText(text)

    def set_text_l(self, text):
        self._l_text = text
        if not self._r:
            self.setText(text)

    def set_func_r(self, func):
        self._r_function = func

    def set_func_l(self, func):
        self._l_function = func
            
    def configure(self, settings):
        self.set_icon_r(settings['icon_r'])
        self.set_icon_l(settings['icon_l'])
        self.set_func_r(settings['func_r'])
        self.set_func_l(settings['func_l'])

    def _f(self):
        return

class BannerLabel(QWidget):
    """
    Label displaying image that resizes according to its parents width while preserving aspect ratio.
    """
    def __init__(self, path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setPixmap(QPixmap(path))
        self.setSizePolicy(SMINMIN)
        self.setMinimumHeight(10) # forces visibility

    def setPixmap(self, p):
        self.p = p
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            w = int(self.rect().width())
            h = int(w * 126/2880)
            rect = QRect(0, 0, w, h)
            painter.drawPixmap(rect, self.p)
            self.setMaximumHeight(h)
            self.setMinimumHeight(h)
