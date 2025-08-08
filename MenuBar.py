"Module for MenuBar class"

from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction

class MenuBar(QMenuBar):

    """
    This class creates a menu bar for the application with File and Help menus.
    """

    def __init__(self, window, app, open_action_handler, options):
        super().__init__(window)
        self.gfm_window = window
        self.options = options

        # File menu
        file_menu = QMenu('File', self)
        open_action = QAction('Open...', self)
        open_action.triggered.connect(open_action_handler)
        file_menu.addAction(open_action)

        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(app.quit)
        file_menu.addAction(exit_action)

        # Tabs menu
        tabs_menu = QMenu('Tabs', self)
        self.continuum_action = QAction('Continuum', self)
        self.continuum_action.triggered.connect(self.show_continuum_options_dialog)
        self.pointing_action = QAction('Pointing', self)
        self.pointing_action.triggered.connect(self.show_pointing_polarization_dialog)
        self.focus_action = QAction('Focus', self)
        self.focus_action.triggered.connect(self.show_focus_polarization_dialog)
        tabs_menu.addAction(self.continuum_action)
        tabs_menu.addAction(self.pointing_action)
        tabs_menu.addAction(self.focus_action)

        self.addMenu(file_menu)
        self.addMenu(tabs_menu)
        self.setNativeMenuBar(False)

        # Help menu
        help_menu = QMenu('Help', self)
        help_action = QAction('Help', self)
        def show_help_dialog():
            QMessageBox.information(window, 'Help', 'Please contact Customer Support')
        help_action.triggered.connect(show_help_dialog)
        help_menu.addAction(help_action)
        self.addMenu(help_menu)

        # Expose actions for external use if needed
        self.open_action = open_action
        self.exit_action = exit_action
        self.help_action = help_action

    def show_pointing_polarization_dialog(self):
        from PointingOptionsDialog import PointingOptionsDialog
        pol = PointingOptionsDialog.get_polarization(self, self.gfm_window.pointing_tab.polarization, self.options)
        print(f"Selected polarization: {pol} setting to window: {self.window}")
        if pol is not None:
            self.gfm_window.pointing_tab.set_polarization(pol)

    def show_focus_polarization_dialog(self):
        from FocusOptionsDialog import FocusOptionsDialog
        pol = FocusOptionsDialog.get_polarization(self, self.gfm_window.focus_tab.polarization, self.options)
        print(f"Selected polarization: {pol} setting to window: {self.window}")
        if pol is not None:
            self.gfm_window.focus_tab.set_polarization(pol)

    def show_continuum_options_dialog(self):
        QMessageBox.information(self, "Continuum Tab", "There are no options for the Continuum tab")