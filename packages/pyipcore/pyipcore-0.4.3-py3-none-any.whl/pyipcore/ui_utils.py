from rbpop import WinManager, RbpopInfo, RbpopWarn, RbpopError
from threading import Thread
import winsound
import time
import re


class BeepThread(Thread):
    def __init__(self):
        # 主程序退出后，子线程也退出
        super().__init__(daemon=True)
        self.tasks = []
        self.flag = True

    def Beep(self, freq, duration):
        self.tasks.append((freq, duration))

    def run(self):
        while self.flag:
            if not self.tasks:
                time.sleep(0.2)
                continue
            freq, duration = self.tasks.pop(0)
            winsound.Beep(freq, duration)

    def stop(self):
        self.flag = False


class BeepWinManager(WinManager):
    def __init__(self):
        super().__init__()
        self.beep = BeepThread()
        self.beep.start()

    def add(self, win, freq, duration):
        super().add(win)
        self.beep.Beep(freq, duration)


_GLOBAL_WM = [None]

def QPop(pop_win_inst, freq=400, duration=100):
    if _GLOBAL_WM[0] is None:
        _GLOBAL_WM[0] = BeepWinManager()

    _GLOBAL_WM[0].add(pop_win_inst, freq, duration)


def _pop_pre(title, msg):
    msg = re.sub(r'(.{30})', r'\1\n', ' ' + msg)
    _len = len(msg)
    ct = 4000 + _len * 50
    return title, msg, ct


def PopInfo(title, msg):
    title, msg, ct = _pop_pre(title, msg)
    QPop(RbpopInfo(msg, title, ct=ct, title_style='color:rgb(105,109,105);font-size:20px;', msg_style='color:rgb(65,98,65);font-size:20px;', close=True), 400, 300)


def PopWarn(title, msg):
    title, msg, ct = _pop_pre(title, msg)
    QPop(RbpopWarn(msg, title, ct=ct, title_style='color:rgb(105,125,85);font-size:20px;', msg_style='color:rgb(85,105,75);font-size:20px;', close=True), 600, 300)


def PopError(title, msg):
    title, msg, ct = _pop_pre(title, msg)
    QPop(RbpopError(msg, title, ct=ct, title_style='color:rgb(225,50,50);font-size:20px;', msg_style='color:rgb(185,50,50);font-size:20px;', close=True), 800, 300)


