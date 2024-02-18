import re

from pyipcore.ipc_utils import *
from files3 import files

VAR_PARAM_TYPE = "param"
VAR_PORT_TYPE = 'port'


class IpCore:
    """
    维护IP核文本
    """

    def __init__(self, dir, name):
        self.fdir = os.path.abspath(dir)
        self.key = name
        self.f = files(self.fdir, IPC_SUFFIX)
        if not self.f[self.key]:
            raise Exception("IP core not found: {}".format(name))

        self._built = None
        self._last_icode = None

    def GetICode(self):
        """Get the instance code of the IP core."""
        return self.icode

    @staticmethod
    def FromVerilog(dir, name, vpath):
        """Trasform a Verilog file into an IP core."""
        f = files(dir, IPC_SUFFIX)
        with open(vpath, encoding='utf-8') as vf:
            content = vf.read()
        f[name] = content

    VERILOG_NUMBER = f"({FT.DIGIT_CHAR}+'{FT.ALPHA})?[0-9_]+"

    def build(self, **params) -> str:
        """Build the IP core with the given parameters."""
        content = self.content
        ft = FT()
        ft.login(lambda key: str(params[key]), *IPC_W_VAL_GS, areas=[IPC_W_VAL_VID])
        ft.login(lambda k, v: (v if params[k] else ""), *IPC_REMOVE_GS, areas=list(IPC_REMOVE_KVID))
        self._built = ft.handle(content)
        return self._built

    # ----------------------------------------- Following are properties -----------------------------------------

    @property
    def content(self):
        """Return the content of the IP core."""
        return self.f[self.key]

    # 获取参数默认值
    @property
    def defaults(self):
        """Return the parameters and values of the IP core."""
        fdict = FDict()
        fdict.login(*IPC_VAL_KVID, *IPC_VAL_GS)  # 参数默认值     \\ $a = 1
        fdict.handle(self.content)
        return fdict

    # 获取参数名称
    @property
    def keys(self):
        """Return the parameters of the IP core."""
        fset = FSet()
        fset.login(IPC_REMOVE_KVID[0], *IPC_REMOVE_GS)  # 分支控制变量   \\ $$a ... $$
        fset.login(IPC_VAL_KVID[0], *IPC_VAL_GS)  # 参数默认值     \\ $a = 1
        fset.handle(self.content)
        return fset

    @property
    def dict(self):
        """Return the parameters of the IP core."""
        fdict = FDict()
        fdict.login(*IPC_VAL_KVID, *IPC_VAL_GS)
        fdict.login(IPC_REMOVE_KVID[0], None, *IPC_REMOVE_GS, val_default=False)
        fdict.handle(self.content)
        return fdict

    @property
    def types(self) -> dict:
        d = self.dict
        return {k: VAR_PARAM_TYPE if d[k] else VAR_PORT_TYPE for k in d}

    @property
    def icode(self):
        """
        Get the instance code of the IP core.
        * Cost lots of time.
        :return:
        """
        _ = create_module_inst_code(self.built)
        self._last_icode = _
        return _

    @property
    def last_icode(self):
        return self._last_icode

    @property
    def built(self):
        if self._built is None:
            self.build(**self.dict)
        return self._built


if __name__ == '__main__':
    IpCore.FromVerilog("", 'test', 'counter.v')
    # raise
    ip = IpCore("", 'test')
    d = ip.dict
    # d['WIDTH'] = 32
    # d['add_clr'] = False
    t = ip.build(**d)
    # save to a counter~.v file
    # with open('counter~.v', 'w', encoding='utf-8') as f:
    #     f.write(t)
    # test = "module Counter #(parameter WIDTH=16,parameter RCO_WIDTH=4"
    # txt = ip.decorate_paragraph(test, 30, 35, "WIDTH", 0)
    # print(txt)
    # txt = ip.decorate_paragraph(txt, 33, 35, "WIDTH", 0)
    print(ip.dict)
    print(ip.types)
    print(ip.icode)
    print(ip._built)
