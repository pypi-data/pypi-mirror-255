from pyipcore.ui_creater.ui_creater import Ui_Form
from pyipcore.ipcore import IpCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QStringListModel, QAbstractListModel, QVariant, QModelIndex, QSize
from PyQt5.QtGui import QIcon, QFont, QTextDocument, QTextCursor
from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox, QWidget, QMainWindow, QComboBox, QLineEdit, QCheckBox, QSizePolicy, QStyledItemDelegate, QMenu, QAction, QLabel, \
    QFrame, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QDialog, QListWidgetItem

from pyipcore.ui_utils import PopWarn, PopError, PopInfo
from pyipcore.ipc_utils import *

from PyQt5.QtWidgets import QInputDialog

MAX_UNDO_REDO = 20


class GUI_IPCreator(QWidget):
    def __init__(self, parent=None):
        super(GUI_IPCreator, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.fpath = None
        self.save_flag = False
        self.ipcore = None

        self.undo_stack = []
        self.redo_stack = []

        self.reset_signals()

    @property
    def ftype(self):
        if self.fpath is None:
            return None
        return os.path.splitext(self.fpath)[1].lower()

    @property
    def keys(self):
        # return list_var items:Str
        return [self.ui.list_var.item(i).text() for i in range(self.ui.list_var.count())]

    def reset_signals(self):
        """
        btn_open
        btn_save
        btn_close  # close file
        btn_new_param
        btn_new_control
        :return:
        """
        self.ui.btn_open.clicked.connect(self.open_file)
        self.ui.btn_save.clicked.connect(self.save_file)
        self.ui.btn_close.clicked.connect(self.close_file)
        self.ui.btn_new_param.clicked.connect(self.new_param)
        self.ui.btn_new_control.clicked.connect(self.new_control)

        # 替换text_code的默认右键菜单
        self.ui.text_code.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_code.customContextMenuRequested.connect(self.open_menu)
        self.ui.text_code.textChanged.connect(lambda: setattr(self, "save_flag", True))

        # list_var double click connect to decorate
        self.ui.list_var.itemClicked.connect(self.decorate_enter)


    def closeEvent(self, event):
        if self.save_flag:
            _ = QMessageBox.question(self, "关闭文件", "是否保存文件？", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if _ == QMessageBox.Yes:
                if not self.save_file():
                    event.ignore()
                    return
            elif _ == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def undo(self):
        if len(self.undo_stack) == 0:
            PopWarn("Warn", "Nothing to undo")
            return
        self.redo_stack.append(self.ui.text_code.toPlainText())
        self.ui.text_code.setPlainText(self.undo_stack.pop())
        if len(self.redo_stack) > MAX_UNDO_REDO:
            self.redo_stack.pop(0)

        self.save_flag = True

    def redo(self):
        if len(self.redo_stack) == 0:
            PopWarn("Warn", "Nothing to redo")
            return
        self.undo_stack.append(self.ui.text_code.toPlainText())
        self.ui.text_code.setPlainText(self.redo_stack.pop())
        if len(self.undo_stack) > MAX_UNDO_REDO:
            self.undo_stack.pop(0)

        self.save_flag = True

    def decorate_enter(self, item):
        self.decorate(self.ui.list_var.indexFromItem(item).row())

    def reload_list(self):
        self.ui.list_var.clear()
        if self.ipcore is None:
            return
        keys = self.ipcore.keys

        # group by lower/upper and sort
        keys = sorted(keys, key=lambda x: (x.islower(), x))

        for key in keys:
            self.ui.list_var.addItem(key)

    def open_file(self):
        f = files(os.getcwd())
        fdir = f["creator_last_dir"]
        fdir = os.path.abspath(fdir) if fdir else os.getcwd()
        # open .v or .ipc
        fpath, _ = QFileDialog.getOpenFileName(self, "Open File", fdir, "IP Core (*.ipc);;Verilog (*.v)")
        if fpath == "":
            return
        self.fpath = fpath
        fdir = os.path.dirname(fpath)
        fnametype = os.path.basename(fpath)
        fname, ftype = os.path.splitext(fnametype)

        if ftype == IPC_SUFFIX:
            # check
            f = files(fdir, IPC_SUFFIX)
            get = f[fname]
            if get is F3False:
                PopError("错误", "IPC文件不存在或无法读取")
                return

            self.ipcore = IpCore(fdir, fname)
            self.ui.text_code.setPlainText(self.ipcore.content)
            self.reload_list()
        elif ftype == '.v':
            # load into text-code
            with open(fpath, encoding='utf-8') as f:
                self.ui.text_code.setPlainText(f.read())
            self.ipcore = None
            self.ui.list_var.clear()
        else:
            PopError("错误", f"不支持的文件类型{ftype}")
            self.fpath = None

        # save last fdir
        f = files(os.getcwd())
        f["creator_last_dir"] = fdir

    def close_file(self):
        if self.fpath is None:
            PopError("错误", "未打开任何文件")
            return
        if self.save_flag:
            _ = QMessageBox.question(self, "关闭文件", "是否保存文件？", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if _ == QMessageBox.Yes:
                if not self.save_file():
                    return
            elif _ == QMessageBox.Cancel:
                return
        self.fpath = None
        self.ipcore = None
        self.ui.text_code.setPlainText("")
        self.ui.list_var.clear()

    def save_file(self):
        # save to .v or .ipc
        if self.fpath is None:
            PopError("错误", "未打开任何文件")
            return
        # ask save path
        fpath, _ = QFileDialog.getSaveFileName(self, "Save File", os.getcwd(), "IP Core (*.ipc);;Verilog (*.v)")
        if fpath == "":
            return

        fdir = os.path.dirname(fpath)
        fnametype = os.path.basename(fpath)
        fname, ftype = os.path.splitext(fnametype)

        # save
        if ftype == IPC_SUFFIX:
            # save to ipc
            f = files(fdir, IPC_SUFFIX)
            f[fname] = self.ui.text_code.toPlainText()
            self.save_flag = False
            # reload for ipc
            self.ipcore = IpCore(fdir, fname)
            self.ui.text_code.setPlainText(self.ipcore.content)
            self.reload_list()
        elif ftype == '.v':
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(self.ui.text_code.toPlainText())
            self.save_flag = False
        else:
            PopError("错误", f"不支持的文件类型{ftype}")
            self.fpath = None

        return True

    def new_param(self):
        if self.fpath is None:
            PopError("错误", "未打开任何文件")
            return
        # ask input: Name:str && Default:str at once
        name, ok = QInputDialog.getText(self, "新建参数", "参数名：")
        if not ok:
            return
        name = name.upper()
        # check name FT.VARIABLE
        if not re.match(FT.VARIABLE, name):
            PopError("错误", "参数名不合法")
            return
        # check name not in list
        if name in self.keys:
            PopError("错误", "参数名已存在")
            return
        default, ok = QInputDialog.getText(self, "新建参数", "默认值：")
        if not ok:
            return
        # do not check
        # add to text-code(first line)  // $name = default
        current_cursor = self.ui.text_code.textCursor()
        self.ui.text_code.moveCursor(QTextCursor.Start)
        self.ui.text_code.insertPlainText(f"// ${name} = {default}\n")
        self.ui.text_code.setTextCursor(current_cursor)
        self.save_flag = True

        # add to list
        self.ui.list_var.addItem(name)

    def new_control(self):
        if self.fpath is None:
            PopError("错误", "未打开任何文件")
            return
        # ask input: Name:str
        name, ok = QInputDialog.getText(self, "新建端口控制", "参数名：")
        if not ok:
            return
        name = name.lower()
        # check name FT.VARIABLE
        if not re.match(FT.VARIABLE, name):
            PopError("错误", "参数名不合法")
            return
        # check name not in list
        if name in self.keys:
            PopError("错误", "参数名已存在")
            return
        # add to list
        self.ui.list_var.addItem(name)

    def decorate(self, i, *args):
        key = self.keys[i]
        mode = 0 if key.islower() else 1

        # get select text (start, end)
        cursor = self.ui.text_code.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        # check
        if start == end:
            PopError("错误", "未选中任何内容.请重试.")
            return

        txt = self.ui.text_code.toPlainText()

        # add to undo_stack
        self.undo_stack.append(txt)
        if len(self.undo_stack) > MAX_UNDO_REDO:
            self.undo_stack.pop(0)
        bef, tar, aft = txt[:start], txt[start:end], txt[end:]

        # 获取tar前面的空白符长度
        bef_space = ""
        _b = re.search(r"(\s+)$", bef)
        _t = re.search(r"^(\s+)", tar)
        if _b is not None:
            _b = _b.group(0)
            bef_space += _b
        if _t is not None:
            _t = _t.group(0)
            bef_space += _t

        # remove \n
        bef_space = bef_space.replace('\n', '')

        if bef_space:
            tar = bef[-len(bef_space):] + tar
            bef = bef[:-len(bef_space)]

        if mode == 0:
            # port
            tar = bef_space + "// $$" + key + "\n" + tar + '\n' + bef_space + "// $$\n"
        else:
            # param
            if re.search("\n.+$", tar) is not None:
                PopError("错误", "Param的选中内容不能跨行.请重试.")
                return
            if '\n' not in tar:
                tar = f"${key}$"
            else:
                tar = f"${key}$\n"

        # replace
        self.ui.text_code.setPlainText(bef + tar + aft)

        self.save_flag = True

        # PopInfo("Info", f"完成{'Param' if mode else 'Port'}操作: {key}.")

    def open_menu(self, pos):
        menu = QMenu(self.ui.text_code)
        keys = self.keys
        fns = []
        # for key in keys:
        #     f = self.wrapper(self.decorate, key)
        #     fns.append(f)

        if len(keys) == 0:
            act = QAction("-- 未打开文件 --", menu)
            menu.addAction(act)
            menu.exec_(self.ui.text_code.mapToGlobal(pos))
            return

        # undo redo sep
        act = QAction("Undo", menu)
        act.triggered.connect(self.undo)
        menu.addAction(act)
        act = QAction("Redo", menu)
        act.triggered.connect(self.redo)
        menu.addAction(act)
        menu.addSeparator()

        for i, key in enumerate(keys):
            if i >= 16:
                act = QAction("-- Too Many --", menu)
                menu.addAction(act)
                break
            act = QAction(key, menu)
            act.triggered.connect(getattr(self, f"decorate_{i}"))
            menu.addAction(act)

        menu.exec_(self.ui.text_code.mapToGlobal(pos))

    def decorate_0(self, *args):
        self.decorate(0, *args)

    def decorate_1(self, *args):
        self.decorate(1, *args)

    def decorate_2(self, *args):
        self.decorate(2, *args)

    def decorate_3(self, *args):
        self.decorate(3, *args)

    def decorate_4(self, *args):
        self.decorate(4, *args)

    def decorate_5(self, *args):
        self.decorate(5, *args)

    def decorate_6(self, *args):
        self.decorate(6, *args)

    def decorate_7(self, *args):
        self.decorate(7, *args)

    def decorate_8(self, *args):
        self.decorate(8, *args)

    def decorate_9(self, *args):
        self.decorate(9, *args)

    def decorate_10(self, *args):
        self.decorate(10, *args)

    def decorate_11(self, *args):
        self.decorate(11, *args)

    def decorate_12(self, *args):
        self.decorate(12, *args)

    def decorate_13(self, *args):
        self.decorate(13, *args)

    def decorate_14(self, *args):
        self.decorate(14, *args)

    def decorate_15(self, *args):
        self.decorate(15, *args)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = GUI_IPCreator()
    w.show()
    sys.exit(app.exec_())
