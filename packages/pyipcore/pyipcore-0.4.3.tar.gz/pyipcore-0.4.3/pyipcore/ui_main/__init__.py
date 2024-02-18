import time

from pyipcore.ui_main.ui_main import Ui_MainForm
from pyipcore.ipcore import IpCore, VAR_PARAM_TYPE, VAR_PORT_TYPE
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QStringListModel, QAbstractListModel, QVariant, QModelIndex, QSize
from PyQt5.QtGui import QIcon, QFont, QTextDocument, QTextCursor
from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox, QWidget, QMainWindow, QComboBox, QLineEdit, QCheckBox, QSizePolicy, QStyledItemDelegate, QMenu, QAction, QLabel, \
    QFrame, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QDialog, QSpacerItem, QScrollBar
from pyipcore.ui_creater import GUI_IPCreator
from pyipcore.ui_utils import PopWarn, PopError, PopInfo
from pyipcore.ipc_utils import *
from files3 import files


class ICodeWorker(QThread):
    icode_update = pyqtSignal(str)

    def __init__(self, dt=0.2):
        super().__init__()
        self._tasks = []
        self._args = []
        self._flag = True
        self._dt = dt

    def run(self):
        while self._flag:
            if len(self._tasks) > 0:
                task = self._tasks.pop(0)
                args = self._args.pop(0)
                _ = task(*args)
                if _ is not None:
                    self.icode_update.emit(str(_))
            time.sleep(self._dt)

    def add(self, task, *args):
        self._tasks.append(task)
        self._args.append(args)

    def stop(self):
        self._flag = False


class VarItemWidget(QWidget):
    """
    _fn: 初始化时传入的回调函数, 具有不定参数
    _data: list of {"var_name", "var_type", "var_value"}
    var_type: "param" or "port"

    # 如果是param模式，那么每一项元素显示为:
        QLabel(var_name) QLineEdit(var_value)
    # 如果是port模式，那么每一项元素显示为:
        QLabel(var_name) QCheckBox(bool(var_value))

    """

    def __init__(self, parent, _fn):
        super(VarItemWidget, self).__init__(parent)
        self._fn = _fn
        self._data = []
        self.widgets = []
        # vlayout(all set to 2)
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(2, 2, 2, 2)
        self.vlayout.setSpacing(2)

    def add(self, vname, vtype, value):
        self._data.append({"var_name": vname, "var_type": vtype, "var_value": value})
        if vtype == VAR_PARAM_TYPE:
            self.addParamItems(self._data[-1])
        elif vtype == VAR_PORT_TYPE:
            self.addPortItems(self._data[-1])
        else:
            raise ValueError(f"Invalid var_type: {vtype}")

    def clearItems(self):
        for w in self.widgets:
            self.vlayout.removeWidget(w)
            w.deleteLater()
        self.widgets.clear()

    def addParamItems(self, vdict: dict):
        """
        create a widget as a capacitor, we can call it 'body'
        create a hlayout(all to 2)
        create a label and a lineedit
        add them to hlayout
        bind lineedit.EditChanged to _fn
        add hlayout to body
        add body to vlayout
        add body to widgets
        :param vdict: dict {'var_name', 'var_value', 'var_type'}
        :return:
        """
        body = QWidget(self)
        hlayout = QHBoxLayout(body)
        hlayout.setContentsMargins(2, 2, 2, 2)
        hlayout.setSpacing(2)
        label = QLabel(body)
        label.setText(vdict["var_name"])
        lineedit = QLineEdit(body)
        lineedit.setText(vdict["var_value"])
        hlayout.addWidget(label)
        hlayout.addWidget(lineedit)
        # lose focus to fn
        lineedit.editingFinished.connect(lambda *args: self._fn(vdict["var_name"], lineedit.text()))
        self.vlayout.addWidget(body)
        self.widgets.append(body)

        if vdict not in self._data:
            self._data.append(vdict)

    def addPortItems(self, vdict: dict):
        """
        create a widget as a capacitor, we can call it 'body'
        create a hlayout(all to 2)
        create a label and a checkbox
        add them to hlayout
        add hlayout to body
        add body to vlayout
        add body to widgets
        :param vdict: dict {'var_name', 'var_value', 'var_type'}
        :return:
        """
        body = QWidget(self)
        hlayout = QHBoxLayout(body)
        hlayout.setContentsMargins(2, 2, 2, 2)
        hlayout.setSpacing(2)
        label = QLabel(body)
        label.setText(vdict["var_name"])
        checkbox = QCheckBox(body)
        checkbox.setChecked(vdict["var_value"])
        hlayout.addWidget(label)
        hlayout.addWidget(checkbox)
        checkbox.stateChanged.connect(lambda x, *args: self._fn(vdict["var_name"], bool(x)))
        self.vlayout.addWidget(body)
        self.widgets.append(body)

        if vdict not in self._data:
            self._data.append(vdict)

    def setFinish(self):
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vlayout.addItem(spacer)


class GUI_Main(QMainWindow):
    def __init__(self):
        super(GUI_Main, self).__init__()
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)
        self.ui.tab_sc.setCurrentIndex(0)

        # add VarItemWidget into var_layout
        self.var_widget = VarItemWidget(self.ui.gbox_var, self._enter_update_vars)
        self.ui.var_layout.addWidget(self.var_widget)

        # close即退出
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)

        # worker
        self.worker = ICodeWorker()
        self.worker.start()
        self.worker.dt = 2

        # vars
        self.ipcore = None
        self.ip_creator = None
        self.var_dict = {}

        # /// customs
        # \t = 4 spaces
        self.ui.ptxt_rc.setTabStopWidth(4 * 4)
        self.ui.ptxt_cc.setTabStopWidth(4 * 4)
        self.ui.ptxt_ic.setTabStopWidth(4 * 4)
        self.reset_signals()

    def reset_signals(self):
        """
        menu_file
            action_file_open
            ...close
            ...quit
        menu_edit
            ...lib_path
        menu_proj
            ...export
        :return:
        """
        self.ui.action_file_open.triggered.connect(self.open_file)
        self.ui.action_file_close.triggered.connect(self.close_file)
        self.ui.action_file_quit.triggered.connect(self.close)
        self.ui.action_proj_export.triggered.connect(self.export_proj)
        self.ui.action_tool_creator.triggered.connect(self.open_creator)

        self.worker.icode_update.connect(self._update_icode)

    def open_creator(self):
        # open as dialog
        if self.ip_creator is not None:
            # 判断是否已经被销毁
            if self.ip_creator.isVisible():
                self.ip_creator.activateWindow()
                return
            else:
                self.ip_creator = None

        self.ip_creator = GUI_IPCreator()
        self.ip_creator.show()




    def _enter_update_vars(self, vname=None, val=None):
        if vname is not None and val is not None:
            self.var_dict[vname] = val
        self.ipcore.build(**self.var_dict)

        # update cc ic
        self.ui.ptxt_cc.setPlainText(self.ipcore.built)
        self.worker.add(self.ipcore.GetICode)
        self.ui.ptxt_ic.setPlainText('loading...')

    def _update_icode(self, txt):
        self.ui.ptxt_ic.setPlainText(txt)

    def open_file(self):
        f = files(os.getcwd())
        fdir = f["last_dir"]
        fdir = os.path.abspath(fdir) if fdir else os.getcwd()
        path = QFileDialog.getOpenFileName(self, "选择IP核文件", fdir, f"IP核文件 (*{IPC_SUFFIX})")[0]
        if not path:
            return
        if not os.path.isfile(path):
            PopError("错误", "路径无效")
            return
        fdir, fnametype = os.path.split(path)
        fname = fnametype[:-len(IPC_SUFFIX)]
        f = files(fdir, IPC_SUFFIX)
        get = f[fname]
        if get is F3False:
            PopError("错误", "IPC文件不存在或无法读取")
            return

        self.ipcore = IpCore(fdir, fname)
        self.ui.ptxt_rc.setPlainText(get)
        self.ui.ptxt_cc.setPlainText("")
        self.ui.ptxt_ic.setPlainText("")
        self.ui.tab_sc.setCurrentIndex(0)

        # model
        self.var_dict = self.ipcore.dict
        self.var_widget.clearItems()
        types = self.ipcore.types
        for var, value in self.var_dict.items():
            _ = {
                "var_name": var,
                "var_type": types[var],
                "var_value": value
            }
            self.var_widget.add(var, types[var], value)
        self.var_widget.setFinish()

        # active worker
        self.worker.dt = 0.2

        self._enter_update_vars()

        # save last fdir
        f = files(os.getcwd())
        f["last_dir"] = fdir

        PopInfo("Info", "打开成功.")

    def close_file(self):
        self.ipcore = None
        self.ui.ptxt_rc.setPlainText("")
        self.ui.ptxt_cc.setPlainText("")
        self.ui.ptxt_ic.setPlainText("")
        self.var_widget.clearItems()
        self.ui.tab_sc.setCurrentIndex(0)

        # deactive worker
        self.worker.dt = 2

    def export_proj(self):
        if self.ipcore is None:
            PopWarn("警告", "请先打开一个IP核文件.")
            return
        f = files(os.getcwd())
        fdir = f["last_export_dir"]
        fdir = os.path.abspath(fdir) if fdir else os.getcwd()
        path = QFileDialog.getSaveFileName(self, "选择导出的.v文件", fdir, f"Verilog文件 (*.v)")[0]
        if not path:
            return

        fdir, fnametype = os.path.split(path)

        # save ipcore.built into file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.ipcore.built)
        PopInfo("Info", "导出成功.")

        # save last fdir
        f = files(os.getcwd())
        f["last_export_dir"] = fdir


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gui = GUI_Main()
    gui.show()
    sys.exit(app.exec_())
