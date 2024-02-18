# -*- coding: utf-8 -*-
from setuptools import setup

PYSIDE_VER = 6

def u(string):
    try:
        return unicode(string)
    except:
        return str(string)

setup(
    name='PySide%s_Customized_Window' % PYSIDE_VER,
    version='1.13',
    description='A customized window based on PySide%s.' % PYSIDE_VER,
    long_description='''## PySide%s-Customized-Window
### 简介 Introduction
本Python模块是PySideX-Customized-Window的PySide%s分支，允许用户创建自定义非客户区窗口，非客户区使用PySide%s绘制，支持移动、最小化、最大化、贴边自动布局、背景模糊等功能。只支持Windows、ReactOS、Wine平台。
<br>
This Python module is the PySide%s branch of PySideX-Customized-Window, allows users to create windows with customized non-client area which are drawn with PySide%s, support moving, minimizing, maximizing, auto-layout of borders, background blurring, etc. It only supports Windows, ReactOS and Wine.
### 安装命令 Installation command
*`python -m pip install PySide%s-Customized-Window`*
### 示例代码 Example code
```
# -*- coding: utf-8 -*-
import sys%s
from PySide%s.QtGui import *
from PySide%s.QtCore import *
from PySide%s_Customized_Window import *
#class MyWindow(BlurWindow):
class MyWindow(CustomizedWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
    def MessageHandler(self, hwnd, message, wParam, lParam):
        print(hwnd, message, wParam, lParam)%s
app = QApplication(sys.argv)
window = MyWindow()
list(map(window.setTitleTextColour, [QColor(0, 0, 139), QColor(119, 235, 255)], [1, 2], [1] * 2))
list(map(window.setMenuButtonColour, [QColor(0, 0, 139), QColor(119, 235, 255)], [1, 2], [1] * 2))
window.setWindowTitle('Window')
window.setDarkTheme(2)
window.setWindowIcon(QIcon('Icon.ico'))
splashscreen = window.splashScreen()
splashscreen.show()
window.resize(*window.getWindowSizeByClientSize([int(400 * window.dpi() / 96.0), int(175 * window.dpi() / 96.0)]))
button = QPushButton('Button', window.clientArea)
window.show()
splashscreen.finish(window)
app.exec%s()
```''' % (PYSIDE_VER, PYSIDE_VER, PYSIDE_VER, PYSIDE_VER, PYSIDE_VER, PYSIDE_VER, ('\nfrom PySide%s.QtWidgets import *' % PYSIDE_VER) if PYSIDE_VER >= 2 else '', PYSIDE_VER if PYSIDE_VER >= 2 else '', PYSIDE_VER if PYSIDE_VER >= 2 else '', PYSIDE_VER, '''
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)''' if PYSIDE_VER >= 2 else '', '' if PYSIDE_VER >= 6 else '_'),
    long_description_content_type='text/markdown',
    url='https://yuzhouren86.github.io',
    author='YuZhouRen86',
    keywords='Python GUI PySide',
    packages=['.'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: Microsoft :: Windows',
        'Development Status :: 5 - Production/Stable',
    ],
    python_requires='>=2.6',
)
