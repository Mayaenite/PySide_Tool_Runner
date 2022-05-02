import subprocess
import os
import sys
import glob

_this_dir = os.path.dirname(__file__)
os.sys.path.append(str(_this_dir))

# Code Path Collection
_code_base_path = os.path.dirname(_this_dir)
_code_base_name = os.path.basename(_code_base_path)

photoshop_prebuild_script  = os.path.join(_this_dir,"PhotoShop_Prep.py")
nuke_build_script          = os.path.join(_this_dir,"Nuke_Contact_Sheet_Builder.py")
photoshop_PDF_Build_script = os.path.join(_this_dir,"PhotoShop_PDF_Build.py")

nuke_cmd_exe = "C:/Program Files/Nuke12.2v3/Nuke12.2.exe -t "

from PySide2 import QtCore, QtUiTools, QtWidgets
QtSlot         = QtCore.Slot
QtSignal       = QtCore.Signal
QtProperty     = QtCore.Property

_UI_Loader = QtUiTools.QUiLoader()


#----------------------------------------------------------------------
def get_folder_Dialog(label="File Finder", UseNativeDialog=False, folder="", parent=None):
	""""""
	options = QtWidgets.QFileDialog.Options()
	if not UseNativeDialog:
		options |= QtWidgets.QFileDialog.DontUseNativeDialog
	if folder == "":
		folder = os.environ["USERPROFILE"]
	folder = QtWidgets.QFileDialog.getExistingDirectory(parent,label,folder, options)
	if folder:
		return folder
	else:
		return False

########################################################################
class Tool_Launcher_UI(QtWidgets.QWidget):
	""""""
	#----------------------------------------------------------------------
	def __init__(self,parent=None):
		"""Constructor"""
		super(Tool_Launcher_UI,self).__init__(parent)
		if False:
			self.Image_Folder_Input   = QtWidgets.QLineEdit()
			self.Find_File_Button     = QtWidgets.QPushButton()
			self.Run_Tool_Button      = QtWidgets.QPushButton()
	#----------------------------------------------------------------------
	def _init(self):
		""""""
	#----------------------------------------------------------------------
	@QtCore.Slot()
	def on_Find_File_Button_clicked(self):
		""""""
		path = get_folder_Dialog()
		if path:
			self.Image_Folder_Input.setText(path)
	#----------------------------------------------------------------------
	@QtCore.Slot()
	def on_Run_Tool_Button_clicked(self):
		""""""
		image_foulder = self.Image_Folder_Input.text()
		if os.path.exists(image_foulder):
			proc = subprocess.Popen('python "{}" "{}"'.format(photoshop_prebuild_script,image_foulder))
			proc.wait()
			nuke_proc = subprocess.Popen('{} "{}" "{}"'.format(nuke_cmd_exe,nuke_build_script,image_foulder))
			nuke_proc.wait()
			PDF_proc = subprocess.Popen('python "{}" "{}"'.format(photoshop_PDF_Build_script,image_foulder))
			PDF_proc.wait()
			
_UI_Loader.registerCustomWidget(Tool_Launcher_UI)

def make_ui():
	Qfile = QtCore.QFile(os.path.join(_this_dir,"main.ui"))
	Qfile.open(QtCore.QFile.ReadOnly)
	ui_wig = _UI_Loader.load(Qfile)
	Qfile.close()
	return ui_wig

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	win = make_ui()
	win._init()
	QtCore.QMetaObject.connectSlotsByName(win)
	win.show()
	sys.exit(app.exec_())