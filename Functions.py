from PyQt5 import QtWidgets
import google_play_scraper as gps
import subprocess
import os


def Ask(self, title, msg):
    bsgbox = QtWidgets.QMessageBox
    answ = bsgbox.question(self, title, msg, bsgbox.Yes | bsgbox.No)

    if answ == bsgbox.Yes:
        return True
    else:
        return False


def AppLookup(package):
    try:
        result = gps.app(package)
        return result['title']
    except gps.exceptions.NotFoundError:
        return False


def ThisDir():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return current_dir


def run(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, shell=True)

    for line in iter(p.stdout.readline, b''):
        yield line.decode('utf8').rstrip()


def about(self, v):
    QAlert = QtWidgets.QMessageBox()
    QAlert.about(self, "About APyK",
                 'APyK v{0} by Pedro Torcatt\n\nIcon by GuillenDesign'.format(v))


def SearchName(self):
    ask = Ask(self, 'App name lookup',
              'Do you want to activate the search for package names? This option will try to search for the app names of the obtained packages. Apps that are not found in the playstore will not be modified. This option needs internet connection and may take longer. Activate?')
    return ask


def ffilter(text, item):
    return text in item


def b(text):
    '''Add bold tags to received text'''
    return '<b>' + text + '</b>'


def bgreen(text):
    '''Add bold tags to received text'''
    return '<b><span style="color:green;">' + text + '</span></b>'


def bred(text):
    '''Add bold tags to received text'''
    return '<b><span style="color:red;">' + text + '</span></b>'
