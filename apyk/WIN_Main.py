import os
import sys

try:
    from apyk.functions import *
    from apyk.ui_backupscreen import Ui_BackupDialog
    from apyk.ui_main import *
except BaseException:
    from functions import *
    from ui_backupscreen import Ui_BackupDialog
    from ui_main import *

version = "0.0.13"


class NewThread(QtCore.QThread):
    '''Thread for install package from wheel'''
    NTSignal = QtCore.pyqtSignal(object)

    def __init__(self, action, param, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.alive = True
        self.action = action
        self.param = param

    def CheckAdb(self):
        '''This is to check if ADB is in the system environment variables'''
        try:
            devnull = open(os.devnull, 'w')
            subprocess.call("adb", stdout=devnull, stderr=devnull)
            return True
        except FileNotFoundError:
            return False

    def run(self):
        '''Run thread'''
        if self.alive == True:
            adb = self.CheckAdb()

            if self.action == 'check':
                if adb == True:
                    out = subprocess.run(['adb', 'devices'],
                                         stdout=subprocess.PIPE)
                    out = out.stdout.decode('utf8')
                    self.NTSignal.emit(out)
                else:
                    self.NTSignal.emit(False)

            elif self.action == 'packages':
                for pkg in run("adb shell pm list packages"):
                    pkg = pkg.split(':')
                    pkg = pkg[1]

                    if self.param == True:
                        name = AppLookup(pkg)
                        if name == False:
                            self.NTSignal.emit(pkg)
                        else:
                            self.NTSignal.emit(pkg + ' | ' + name)
                    else:
                        self.NTSignal.emit(pkg)

            elif self.action == 'backup':
                for pkg in self.param[0]:
                    results = []
                    for out in run("adb shell pm path {0}".format(pkg)):
                        results.append(out)

                    if len(results) > 1:  # more than one apk, so, select named base.apk
                        target = [apk for apk in results if 'base' in apk][0]
                    else:  # select the only apk
                        target = results[0]

                    # Split package word
                    target = target.split('package:')[1]

                    self.NTSignal.emit(b('Current package: ') + pkg)
                    self.NTSignal.emit(b('APK path: ') + target)

                    for out in run(r"adb pull {0} {1}\\{2}".format(target, self.param[1], pkg)):
                        if 'does not exist' in out:
                            self.NTSignal.emit(
                                b('Status: ') + bred('Remote object does not exist'))
                        else:
                            self.NTSignal.emit(
                                b('Status: ') + bgreen('Successfully exported'))
                    self.NTSignal.emit('---------')
                    self.NTSignal.emit('Step')


class BackupWindow(QtWidgets.QDialog, Ui_BackupDialog):
    '''Window for processing selected packages'''

    def __init__(self, parent, items):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ThisDir(), 'icon.ico')))
        self.items = items
        self.SetLabelCount()
        self.SetBarConfig()
        self.count = 0
        self.canStart = True
        self.Destiny = ''
        self.RequestFolder()
        # Create Thread Class for allow access from other methods
        if self.canStart == True:
            self.CollectThread = NewThread(
                'backup', [self.items, self.Destiny])
            self.StartBackup()
        else:
            self.Cancelled()

    def StartBackup(self):
        self.CollectThread.NTSignal.connect(self.BackupTHROut)
        self.CollectThread.finished.connect(self.AfterBackup)
        self.CollectThread.start()
        self.curr_process.setText('Backing up')

    def RequestFolder(self):
        dest = GetDestiny(self)
        if dest == False:
            self.canStart = False
        else:
            self.Destiny = dest

    def Cancelled(self):
        self.curr_process.setText('The backup process has been cancelled')

    def BackupTHROut(self, output):
        if not 'Step' in output:  # Show output in 'Console'
            self.out.append(output)
        elif 'Step' in output:  # Modify progressbar status
            self.count += 1
            self.progressBar.setValue(self.count)

    def AfterBackup(self):
        self.CollectThread.alive = False
        self.curr_process.setText('Finished')

    def SetLabelCount(self):
        '''Assign number of packets to be processed to the label'''
        self.pkgs_count.setText(str(len(self.items)))

    def SetBarConfig(self):
        self.progressBar.setMaximum(len(self.items))

    def closeEvent(self, event):
        if hasattr('self', 'CollectThread'):
            if self.CollectThread.alive == True:
                ask = Ask(
                    self, 'Exit?', 'There is a process in place, are you sure you want to leave?')

                if ask == True:
                    self.CollectThread.alive = False
                    self.CollectThread.wait()
                    event.accept()
                else:
                    event.ignore()
        else:
            event.accept()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    '''Main window class'''

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ThisDir(), 'icon.ico')))
        self.list_pkgs.itemSelectionChanged.connect(self.ShowSelected)
        self.filter_box.textChanged.connect(self.FilterPkgs)
        self.btn_backup.clicked.connect(self.StartBackup)
        self.actionAbout.triggered.connect(lambda: about(self, version))
        self.closeEvent = self.closeEvent

        self.selected_pkgs.setHidden(True)
        self.btn_backup.setHidden(True)
        self.status_label.setHidden(True)

        self.Continue = True
        self.DoingSomething = False
        self.AppLookup = False

        act = SearchName(self)
        if act == True:
            self.AppLookup = True

        self.CheckDevice()

    def closeEvent(self, event):
        if self.DoingSomething == True:
            ask = Ask(
                self, 'Exit?', 'There is a process in place, are you sure you want to leave?')

            if ask == True:
                sys.exit()
            else:
                event.ignore()

    def StartBackup(self):
        '''This starts the backup process, assigns the selected packets to a list and sends them to the window where they will be processed.'''
        pkgs = []
        for row in range(self.selected_pkgs.count()):
            itemobj = self.selected_pkgs.item(row)
            item = itemobj.text()
            pkgs.append(item)
        BW = BackupWindow(self, pkgs)
        BW.show()

    def StatusLab(self, text):
        '''Displays the status label and assigns the received text to it'''
        self.status_label.setHidden(False)
        self.status_label.setText(text)

    def CheckDevice(self):
        '''Start the thread to check the connected devices'''
        self.StatusLab('Checking device...')
        self.CheckThread = NewThread('check', None)
        self.CheckThread.NTSignal.connect(self.CheckTHROutput)
        self.CheckThread.finished.connect(self.AfterCheck)
        self.CheckThread.start()
        self.DoingSomething = True

    def CheckTHROutput(self, output):
        '''Gets the output of the device check thread'''
        if output == False:  # error with adb command
            self.Continue = False
            self.StatusLab("ADB was not detected")
        else:
            if '\tdevice' in output:
                device = [int(s) for s in output.split() if s.isdigit()]
                if len(device) == 1:
                    self.field_device.setText(str(device[0]))
                else:
                    self.Continue = False
                    self.StatusLab(
                        'More than one device has been detected')
            else:
                self.Continue = False
                if 'unauthorized' in output:
                    self.StatusLab('Device unauthorized')
                else:
                    self.StatusLab('No device detected')

    def AfterCheck(self):
        self.DoingSomething = False
        '''Executed at the end of the device check thread'''
        # Continue is temporal, maybe is better show an alert an exit
        if self.Continue == True:
            self.GetPackages()

    def GetPackages(self):
        '''Start the thread to get the packets from the connected device'''
        self.StatusLab('Searching packages...')
        self.GetPkgsThread = NewThread('packages', self.AppLookup)
        self.GetPkgsThread.NTSignal.connect(self.ShowOutput)
        self.GetPkgsThread.finished.connect(self.AfterPackages)
        self.GetPkgsThread.start()
        self.DoingSomething = True

    def ShowOutput(self, out):
        '''Method for show console output in each Thread call'''
        self.list_pkgs.addItem(out)

    def AfterPackages(self):
        self.DoingSomething = False
        '''Runs at the end of the thread to get the packets from the connected device'''
        self.filter_box.setEnabled(True)
        self.status_label.setHidden(True)

        self.select_all.setEnabled(True)
        self.deselect_all.setEnabled(True)
        self.clear_filter.setEnabled(True)

    def FilterPkgs(self, text):
        '''Filters the list of packets based on the given text'''
        for row in range(self.list_pkgs.count()):
            itemobj = self.list_pkgs.item(row)
            item = itemobj.text()
            if text:
                itemobj.setHidden(not ffilter(text, item))
            else:
                itemobj.setHidden(False)

    def ShowSelected(self):
        '''It is executed each time an item is selected from the list of packages and is displayed in a list part'''
        listwid = self.list_pkgs
        selcwid = self.selected_pkgs
        selected = listwid.selectedItems()
        if len(selected) != 0:
            self.selected_pkgs.setHidden(False)
            self.btn_backup.setHidden(False)
            selcwid.clear()
            for x in selected:
                selcwid.addItem(x.text().split(' | ')[0])
        else:
            self.selected_pkgs.setHidden(True)
            self.btn_backup.setHidden(True)


def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
