from PySide6.QtWidgets import QDialog, QMessageBox

from ContCalibOptionsDialog import ContCalibOptionsDialog

class FocusOptionsDialog(ContCalibOptionsDialog):
    def __init__(self, parent=None, polarization=None):
        super().__init__("Focus", parent, polarization)


    @staticmethod
    def get_polarization(parent, polarization):
        dialog = FocusOptionsDialog(parent, polarization)
        result = dialog.exec()
        if result == QDialog.Accepted:
            pol = 'X' if dialog.radio_x.isChecked() else 'Y'
            QMessageBox.information(parent or dialog, "Focus Tab", f"You chose {pol} polarization.")
            return pol
        return None