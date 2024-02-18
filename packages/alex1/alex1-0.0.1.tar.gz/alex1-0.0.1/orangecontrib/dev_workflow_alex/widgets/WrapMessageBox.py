import os

import shared_variables
from PyQt5 import QtWidgets

def create_message_box(text, window_title, detailed_text):
    """
    This function creates a message box with provided text, window title, and detailed text.
    It is used to display informative messages to the user.
    """
    msg = QtWidgets.QMessageBox()
    msg.setText(text)
    msg.setWindowTitle(window_title)
    msg.setDetailedText(detailed_text)
    retval = msg.exec_()

def create_message_box_question_yes_no(text):
    """
    This function creates a question box with the provided text.
    The user can respond with "Yes" or "No".
    If the user responds with "Yes", the function returns True; otherwise, it returns False.
    """
    response = QtWidgets.QMessageBox.question(None, "", text, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    if response == QtWidgets.QMessageBox.Yes:
        return True
    return False

# Return filename; '' -> nothing selected
# Extensions are separated by space
def get_file_windows(self_arg, extension="*.txt *.png *.xls"):
    """
    This function opens a file selection dialog and returns the path of the selected file.
    The 'extension' argument allows specifying allowed file extensions for selection.
    """
    file_name = QtWidgets.QFileDialog.getOpenFileName(self_arg,
                                                      str("Select one file"), os.path.dirname(shared_variables.current_ows), str("File format (" + extension + ")"))
    return file_name[0]

def save_file_windows(self_arg, type_out="All Files (*);;Text Files (*.txt)"):
    """
    This function opens a file save dialog and returns the path where the user wants to save a file.
    The 'type_out' argument allows specifying the allowed file types for saving.
    """
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self_arg, "Save file in", "", type_out, options=options)
    return file_name
