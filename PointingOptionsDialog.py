"Dialog for choosing polarization in the Pointing tab."

from PySide6.QtWidgets import QDialog, QMessageBox

from ContCalibOptionsDialog import ContCalibOptionsDialog

class PointingOptionsDialog(ContCalibOptionsDialog):
    def __init__(self, parent, polarization, options):
        super().__init__("Pointing", parent, polarization, options)


    @staticmethod
    def get_polarization(parent, polarization, options):
        dialog = PointingOptionsDialog(parent, polarization, options)
        result = dialog.exec()
        if result == QDialog.Accepted:
            checked_btn = dialog.polarization_group.checkedButton()
            pol = dialog.polarization_button_map.get(checked_btn, None)
            if pol:
                QMessageBox.information(parent or dialog, "Pointing Tab", f"You chose {pol} polarization.")
            return pol
        return None
