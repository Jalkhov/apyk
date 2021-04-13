from UI_Main import *
from UI_BackupScreen import Ui_BackupDialog
from Functions import *
import sys
import os

version = "0.0.1"


class NewThread(QtCore.QThread):
    '''Thread for install package from wheel'''
    NTSignal = QtCore.pyqtSignal(object)

    def __init__(self, action, param, parent=None):
        QtCore.QThread.__init__(self, parent)
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

        elif self.action == 'collect_apks':
            for pkg in self.param:
                results = []
                for out in run("adb shell pm path {0}".format(pkg)):
                    results.append(out)
                self.NTSignal.emit(results)

        elif self.action == 'pull_apks':
            pkgs = self.param
            for pkg in pkgs:
                for out in run(r"adb pull {0} apks\\{1}".format(pkgs[pkg], pkg)):
                    # pass
                    self.NTSignal.emit(out)


class BackupWindow(QtWidgets.QDialog, Ui_BackupDialog):
    '''Window for processing selected packages'''

    def __init__(self, parent, items):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ThisDir(), 'icon.png')))
        self.DoingSomething = False
        self.items = items
        self.itcount = len(items)
        self.SetLabelCount()
        self.SetBarConfig()
        self.collected = {}
        self.count1 = 0
        self.count2 = 0
        self.StartBackup()

    def SetLabelCount(self):
        '''Assign number of packets to be processed to the label'''
        self.pkgs_count.setText(str(self.itcount))

    def SetBarConfig(self):
        self.progressBar.setMaximum(self.itcount * 2)

    def StartBackup(self):
        # Posibilidad de elegir un directorio para guardar backup
        self.CollectThread = NewThread('collect_apks', self.items)
        self.CollectThread.NTSignal.connect(self.CollectTHROut)
        self.CollectThread.finished.connect(self.AfterCollect)
        self.CollectThread.start()
        self.DoingSomething = True

        self.curr_process.setText('Collecting APKs')
        self.out.append(b(':::: Collecting APKs ::::'))
        self.out.append('')

    def CollectTHROut(self, output):
        self.count1 += 1
        target = ''
        if len(output) > 1:  # more than one apk, so, select named base.apk
            target = [apk for apk in output if 'base' in apk][0]
        else:  # select the only apk
            target = output[0]

        # Split package word
        target = target.split('package:')[1]

        # Get current package
        curritem = self.items[self.count1 - 1]

        # Append target to collected variable
        self.collected[curritem] = target

        self.out.append(b('Current package: ') + curritem)
        self.out.append(b('APK path: ') + target)
        self.out.append('')

        self.progressBar.setValue(self.count1)

    def AfterCollect(self):
        self.curr_process.setText('Exporting APKs')
        self.out.append(b(':::: Export process started ::::'))
        self.out.append('')

        self.PullThread = NewThread('pull_apks', self.collected)
        self.PullThread.NTSignal.connect(self.PullTHROut)
        self.PullThread.finished.connect(self.AfterPull)
        self.PullThread.start()

    def PullTHROut(self, output):
        self.count1 += 1
        self.count2 += 1
        curritem = self.items[self.count2 - 1]
        self.progressBar.setValue(self.count1)
        if 'does not exist' in output:
            self.out.append(b('{0}: '.format(curritem)) +
                            bred('Remote object does not exist'))
        else:
            self.out.append(b('{0}: '.format(curritem)) +
                            bgreen('Successfully exported'))

    def AfterPull(self):
        self.DoingSomething = False
        self.curr_process.setText('Finished')
        self.out.append('')
        self.out.append(b('Finished'))

    def closeEvent(self, event):
        if self.DoingSomething == True:
            bsgbox = QtWidgets.QMessageBox
            ret = bsgbox.question(
                self, 'Exit?', 'There is a process in place, are you sure you want to leave?', bsgbox.Yes | bsgbox.No)

            if ret == bsgbox.Yes:
                event.accept()  # let the window close
            else:
                event.ignore()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    '''Main window class'''

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.closeEvent = self.closeEvent
        self.setWindowIcon(QtGui.QIcon(os.path.join(ThisDir(), 'icon.png')))
        self.list_pkgs.itemSelectionChanged.connect(self.ShowSelected)
        self.filter_box.textChanged.connect(self.FilterPkgs)
        self.btn_backup.clicked.connect(self.StartBackup)
        self.actionAbout.triggered.connect(lambda: about(self, version))
        self.selected_pkgs.setHidden(True)
        self.btn_backup.setHidden(True)
        self.status_label.setHidden(True)
        self.Continue = True
        self.DoingSomething = False
        self.AppLookup = False
        self.CheckDevice()

    def closeEvent(self, event):
        if self.DoingSomething == True:
            bsgbox = QtWidgets.QMessageBox
            ret = bsgbox.question(
                self, 'Exit?', 'There is a process in place, are you sure you want to leave?', bsgbox.Yes | bsgbox.No)

            if ret == bsgbox.Yes:
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
                print(device)
                if len(device) == 1:
                    # Ask if make App name lookup
                    act = SearchName(self)
                    if act == True:
                        self.AppLookup = True

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


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

    """
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
    sys.exit(app.exec_())
    """
