# PYTHON_ARGCOMPLETE_OK

from .app import *


class AppUniws(App):
    def __init__(self) -> 'None':
        super().__init__(name='uniws',
                         help='The main uniws application.')
        self.apps.append(AppInit())
        self.apps.append(AppHardware())
        self.apps.append(AppSoftware())


def uniws() -> 'None':
    main(AppUniws())


def uhc() -> 'None':
    main(AppHardware.connect(False))


def uhp() -> 'None':
    main(AppHardware.power(False))


def uhu() -> 'None':
    main(AppHardware.upload(False))


def uhd() -> 'None':
    main(AppHardware.download(False))


def uhs() -> 'None':
    main(AppHardware.shell(False))


def uhw() -> 'None':
    main(AppHardware.watch(False))


def uha() -> 'None':
    main(AppHardware.action(False))


def usf() -> 'None':
    main(AppSoftware.fetch(False))


def usb() -> 'None':
    main(AppSoftware.build(False))


def usi() -> 'None':
    main(AppSoftware.install(False))


def ust() -> 'None':
    main(AppSoftware.test(False))


def usr() -> 'None':
    main(AppSoftware.release(False))


def usc() -> 'None':
    main(AppSoftware.clean(False))


def usp() -> 'None':
    main(AppSoftware.purge(False))


def usa() -> 'None':
    main(AppSoftware.action(False))
