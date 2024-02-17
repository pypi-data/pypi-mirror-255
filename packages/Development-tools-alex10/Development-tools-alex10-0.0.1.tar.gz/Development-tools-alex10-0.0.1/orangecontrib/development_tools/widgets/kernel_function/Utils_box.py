import os

import shared_variables
from PyQt5 import QtWidgets

def create_message_box(Text, WindowTitle, DetailedText):
    """
    This function creates a message box with provided text, window title, and detailed text.
    It is used to display informative messages to the user.
    """
    msg = QtWidgets.QMessageBox()
    msg.setText(Text)
    msg.setWindowTitle(WindowTitle)
    msg.setDetailedText(DetailedText)
    retval = msg.exec_()

def create_message_box_question_yes_no(Text):
    """
    This function creates a question dialog box with the provided text.
    The user can respond with "Yes" or "No".
    If the user responds "Yes", the function returns True, otherwise, it returns False.
    """
    response = QtWidgets.QMessageBox.question(None, "", Text, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    if response == QtWidgets.QMessageBox.Yes:
        return True
    return False

# return filename; '' -> nothing selected
# extension separated by space
def get_file_windows(self_arg, extension="*.txt *.png *.xls"):
    """
    This function opens a file selection dialog and returns the path of the selected file.
    The extension argument allows specifying allowed file extensions for selection.
    """
    fileName = QtWidgets.QFileDialog.getOpenFileName(self_arg,
                                                     str("Select one file"), os.path.dirname(shared_variables.current_doc),
                                                     str("file format (" + extension + ")"))
    return fileName[0]

def save_file_windows(self_arg, type_out="All Files (*);;Text Files (*.txt)"):
    """
    This function opens a file save dialog and returns the path of the file where the user wants to save a file.
    The type_out argument allows specifying the allowed file types for saving.
    """
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self_arg, "Save file in", "", type_out, options=options)
    return fileName
