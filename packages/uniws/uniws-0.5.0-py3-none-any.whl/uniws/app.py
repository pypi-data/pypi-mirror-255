from .user import *

if DIR_UWS:
    from hardware import hardware
    from software import software
else:
    def hardware() -> 'list[Hardware] | Hardware':
        return []

    def software() -> 'list[Software]':
        return []


class Command(App):
    def __init__(
        self,
        uws: 'bool',
        name: 'str' = None,
        help: 'str' = None,
        prolog: 'str' = None,
        epilog: 'str' = None,
    ) -> 'None':
        super().__init__(name=name,
                         help=help,
                         prolog=prolog,
                         epilog=epilog)
        self.__uws = uws

    def __call__(
        self,
        args: 'dict[Arg]' = None,
        apps: 'list[App]' = None,
    ) -> 'None':
        super().__call__(args, apps)
        if self.__uws and not DIR_UWS:
            raise RuntimeError(
                'This command is available only inside uniws workspace.')


class Subcommand(App):
    def __init__(
        self,
        sub: 'bool',
        apps: 'list[App]',
        name: 'str' = None,
        help: 'str' = None,
        prolog: 'str' = None,
        epilog: 'str' = None,
    ) -> 'None':
        self.cmd = name
        self.list: 'list[App]' = []
        self.error = None
        for app in apps:
            if getattr(app, name):
                self.list.append(app)
        if not self.list:
            self.error = RuntimeError(f'Nothing supports {name}.')
        if len(apps) == 1 and self.list:
            app = self.list[0]
            subapp: 'App' = getattr(self.list[0], name)
            super().__init__(name=(name if sub else None),
                             help=subapp.help or app.help or help,
                             prolog=subapp.prolog or app.prolog or prolog,
                             epilog=subapp.epilog or app.epilog or epilog)
            self.args.extend(subapp.args)
            self.apps.extend(subapp.apps)
            # Substitute software with the corresponding subcommand.
            self.list[0] = subapp
        else:
            super().__init__(name=(name if sub else None),
                             help=help,
                             prolog=prolog,
                             epilog=epilog)
            for app in self.list:
                subapp: 'App' = getattr(app, name)
                newapp = App(name=app.name,
                             help=subapp.help or app.help,
                             prolog=subapp.prolog or app.prolog,
                             epilog=subapp.epilog or app.epilog)
                newapp.args.extend(subapp.args)
                newapp.apps.extend(subapp.apps)
                self.apps.append(newapp)

    def __call__(
        self,
        args: 'dict[Arg]' = None,
        apps: 'list[App]' = None,
    ) -> 'None':
        super().__call__(args, apps)
        if self.error:
            raise self.error
        if len(self.list) == 1:
            self.list[0](args, apps)
        else:
            app = apps[3 if self.name else 1]
            for x in self.list:
                if x.name == app.name:
                    app = x
                    break
            getattr(app, self.cmd)(args, apps)


class AppInit(Command):
    def __init__(self) -> 'None':
        super().__init__(False,
                         name='init',
                         help='Initialize an empty uniws workspace.')
        self.arg_remote = Arg(name='URI',
                              sopt='r',
                              lopt='remote',
                              help='A Git remote to set as the origin.')
        self.args.append(self.arg_remote)
        self.arg_branch = Arg(name='NAME',
                              sopt='b',
                              lopt='branch',
                              help='A Git branch to set as main.')
        self.args.append(self.arg_branch)
        self.arg_dir = Arg(name='DIR',
                           count='?',
                           default=os.path.abspath('.'),
                           help=str('A non-existing or empty directory. '
                                    'Defaults to the current one.'))
        self.args.append(self.arg_dir)

    def __call__(
        self,
        args: 'dict[Arg]' = None,
        apps: 'list[App]' = None,
    ) -> 'None':
        super().__call__(args, apps)
        dir = os.path.abspath(args[self.arg_dir])
        if os.path.exists(dir):
            if os.path.isdir(dir):
                if len(os.listdir(dir)) != 0:
                    raise RuntimeError(f'Directory not empty: {dir}')
            else:
                raise RuntimeError(f'Not a directory: {dir}')
        else:
            os.makedirs(dir, 0o755)
        branch = args[self.arg_branch]
        branch = f'-b {branch}' if branch else ''
        remote = args[self.arg_remote]
        remote = f'git remote add origin {remote}' if remote else 'true'
        sh(f'true'
           f' && cp -RaT {os.path.dirname(__file__)}/template {dir}'
           f' && cd {dir}'
           f' && git init {branch}'
           f' && {remote}'
           f' && git add -A'
           f' && git commit -m "Initial commit"'
           f';')


class AppSoftware(Command):
    APPS = software()

    def __init__(self) -> None:
        super().__init__(True,
                         name='sw',
                         help='Manipulate software.')
        self.apps.append(AppSoftware.fetch(True))
        self.apps.append(AppSoftware.build(True))
        self.apps.append(AppSoftware.install(True))
        self.apps.append(AppSoftware.test(True))
        self.apps.append(AppSoftware.release(True))
        self.apps.append(AppSoftware.clean(True))
        self.apps.append(AppSoftware.purge(True))
        self.apps.append(AppSoftware.action(True))

    @staticmethod
    def fetch(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='fetch',
                          help='Fetch the sources.')

    @staticmethod
    def build(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='build',
                          help='Build the software from the sources.')

    @staticmethod
    def install(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='install',
                          help='Install the built software.')

    @staticmethod
    def test(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='test',
                          help='Test the installed software.')

    @staticmethod
    def release(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='release',
                          help='Release the software.')

    @staticmethod
    def clean(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='clean',
                          help='Delete the built software.')

    @staticmethod
    def purge(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='purge',
                          help='Delete the sources.')

    @staticmethod
    def action(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppSoftware.APPS,
                          name='action',
                          help='Perform a custom action on the software.')


class AppHardware(Command):
    APPS = hardware()

    def __init__(self) -> None:
        super().__init__(True,
                         name='hw',
                         help='Manipulate hardware.')
        self.apps.append(AppHardware.connect(True))
        self.apps.append(AppHardware.power(True))
        self.apps.append(AppHardware.upload(True))
        self.apps.append(AppHardware.download(True))
        self.apps.append(AppHardware.shell(True))
        self.apps.append(AppHardware.watch(True))
        self.apps.append(AppHardware.action(True))

    @staticmethod
    def connect(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='connect',
                          help='Change state of connection to the hardware.')

    @staticmethod
    def power(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='power',
                          help='Change power state of the hardware.')

    @staticmethod
    def upload(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='upload',
                          help='Upload files to the hardware.')

    @staticmethod
    def download(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='download',
                          help='Download files from the hardware.')

    @staticmethod
    def shell(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='shell',
                          help='Execute a command or start the shell in an interactive mode.')

    @staticmethod
    def watch(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='watch',
                          help='Watch the hardware live stream.')

    @staticmethod
    def action(sub: 'bool') -> 'App':
        return Subcommand(sub,
                          AppHardware.APPS,
                          name='action',
                          help='Perform a custom action on the hardware.')
