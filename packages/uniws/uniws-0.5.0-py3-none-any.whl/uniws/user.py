import os
import subprocess
import sys
from argapp import *


def __pwd() -> 'str':
    return os.path.abspath(os.getenv('PWD'))


def __root() -> 'str':
    result = __pwd()
    while result != '/':
        if os.path.exists(f'{result}/.uniws'):
            return result
        result = os.path.dirname(result)
    return ''


DIR_PWD = __pwd()
DIR_UWS = __root()
DIR_UNI = f'{DIR_UWS}/.uniws'
DIR_BIN = f'{DIR_UWS}/bin'
DIR_ETC = f'{DIR_UWS}/etc'
DIR_LIB = f'{DIR_UWS}/lib'
DIR_TMP = f'{DIR_UWS}/tmp'

if DIR_UWS:
    sys.path.insert(0, f'{DIR_UWS}/.uniws')
    from shell import shell_bin, shell_src
else:
    def shell_bin() -> 'str':
        return '/bin/sh'

    def shell_src() -> 'str':
        return ''


class Software(App):
    def __init__(
        self,
        name: 'str',
        help: 'str' = '',
        prolog: 'str' = '',
        epilog: 'str' = '',
    ) -> 'None':
        super().__init__(name=name,
                         help=help,
                         prolog=prolog,
                         epilog=epilog)
        self.fetch: 'App' = None
        self.build: 'App' = None
        self.install: 'App' = None
        self.test: 'App' = None
        self.release: 'App' = None
        self.clean: 'App' = None
        self.purge: 'App' = None
        self.action: 'App' = None


class Hardware(App):
    def __init__(
        self,
        name: 'str',
        help: 'str' = '',
        prolog: 'str' = '',
        epilog: 'str' = '',
    ) -> 'None':
        super().__init__(name=name,
                         help=help,
                         prolog=prolog,
                         epilog=epilog)
        self.connect: 'App' = None
        self.power: 'App' = None
        self.upload: 'App' = None
        self.download: 'App' = None
        self.shell: 'App' = None
        self.watch: 'App' = None
        self.action: 'App' = None


class ShellResult:
    def __init__(
        self,
        cmd: 'str',
        out: 'str',
        code: 'int',
    ) -> 'None':
        self.__cmd = cmd
        self.__out = out
        self.__code = code

    @property
    def cmd(self) -> 'str':
        return self.__cmd

    @property
    def out(self) -> 'str':
        return self.__out

    @property
    def code(self) -> 'int':
        return self.__code


class ShellError(BaseException):
    def __init__(self, res: 'ShellResult') -> 'None':
        super().__init__(res)
        self.__res = res

    def __str__(self) -> 'str':
        return f'Command failed with exit code {self.code}:\n{self.cmd}'

    @property
    def cmd(self) -> 'str':
        return self.__res.cmd

    @property
    def out(self) -> 'str':
        return self.__res.out

    @property
    def code(self) -> 'int':
        return self.__res.code


def sh(
    cmd: 'str',
    capture: 'bool' = False,
    check: 'bool' = True,
) -> 'ShellResult':
    _sh = f'{DIR_UNI}/{shell_src()}'
    if os.path.isfile(_sh):
        cmd = f'source {_sh};\n{cmd}'
    elif DIR_UWS:
        PATH = f'export PATH={DIR_BIN}:{DIR_LIB}:$PATH'
        PYTHONPATH = f'export PYTHONPATH={DIR_LIB}:$PYTHONPATH'
        LD_LIBRARY_PATH = f'export LD_LIBRARY_PATH={DIR_LIB}:$LD_LIBRARY_PATH'
        cmd = f'{PATH};\n{PYTHONPATH};\n{LD_LIBRARY_PATH};\n{cmd}'
    cmd = f'shopt -s expand_aliases;\n{cmd}'
    args = [cmd]
    kwargs = {
        'shell': True,
        'universal_newlines': True,
        'executable': shell_bin(),
    }
    if capture:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.STDOUT
    proc = subprocess.Popen(*args, **kwargs)
    proc.wait()
    result = ShellResult(cmd=cmd,
                         out=('' if not capture else proc.stdout.read()),
                         code=proc.returncode)
    if check and result.code != 0:
        raise ShellError(result)
    return result
