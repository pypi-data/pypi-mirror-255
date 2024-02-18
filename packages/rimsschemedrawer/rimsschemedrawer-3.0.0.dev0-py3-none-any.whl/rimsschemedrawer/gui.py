"""GUI Application for plotting RIMS schemes."""

import importlib.metadata
import json
from pathlib import Path

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

try:
    from qtpy import QtCore, QtGui, QtWidgets
except ImportError as e:
    raise ImportError(
        "ImportError: No GUI environment found. "
        "Please install this package with 'pip install rimsschemedrawer[gui]'"
    ) from e

from rimsschemedrawer.plotter import Plotter
import rimsschemedrawer.utils as ut


class SchemeDrawer(QtWidgets.QMainWindow):
    """RIMSSchemeDrawer."""

    def __init__(self):
        # run in debug mode?
        self.rundebug = False

        # program info
        self.author = "Reto Trappitsch"
        self.version = importlib.metadata.version("rimsschemedrawer")

        # user settings - maybe to be remembered at some point
        self.user_path = Path.home()

        # initialize the thing
        super().__init__()
        self.title = "RIMS Scheme Drawer"
        self.left = 50
        self.top = 80
        self.width = 20
        self.height = 20

        # initialize the UI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # settings:
        self.numberofsteps = 7
        self.lineedit_size = QtCore.QSize(100, 20)

        # entries and labels necessary
        self.rbtngrp_units = QtWidgets.QButtonGroup()
        self.rbtn_nm = QtWidgets.QRadioButton("nm")
        self.rbtn_cm = QtWidgets.QRadioButton()
        self.lbl_steps = []
        self.edt_level = []
        self.edt_term = []
        self.edt_gslevel = QtWidgets.QLineEdit()
        self.edt_gsterm = QtWidgets.QLineEdit()
        self.edt_iplevel = QtWidgets.QLineEdit()
        self.edt_ipterm = QtWidgets.QLineEdit()
        self.chk_lowlying = []
        self.chk_forbidden = []

        # settings line edits
        self.edt_sett_figwidth = QtWidgets.QLineEdit()
        self.edt_sett_figheight = QtWidgets.QLineEdit()
        self.edt_sett_fstitle = QtWidgets.QLineEdit()
        self.edt_sett_fsaxes = QtWidgets.QLineEdit()
        self.edt_sett_fsaxlbl = QtWidgets.QLineEdit()
        self.chk_sett_linebreaks = QtWidgets.QCheckBox("Line breaks?")
        self.chk_sett_showcmax = QtWidgets.QCheckBox()  # no label -> label in layout
        self.chk_sett_showcmax.setChecked(True)
        self.chk_sett_showevax = QtWidgets.QCheckBox("Show eV axis labels?")
        self.chk_sett_showevax.setChecked(True)
        self.edt_sett_fslbl = QtWidgets.QLineEdit()
        self.edt_sett_headspace = QtWidgets.QLineEdit()
        self.edt_sett_arrwidth = QtWidgets.QLineEdit()
        self.edt_sett_arrheadwidth = QtWidgets.QLineEdit()
        self.edt_sett_preclambda = QtWidgets.QLineEdit()
        self.edt_sett_preclevel = QtWidgets.QLineEdit()
        self.rbtngrp_iplabel = QtWidgets.QButtonGroup()
        self.rbtn_iplable_top = QtWidgets.QRadioButton("Top")
        self.rbtn_iplable_bottom = QtWidgets.QRadioButton("Bott.")
        self.rbtngrp_sett_forbidden = QtWidgets.QButtonGroup()
        self.rbtn_sett_xoutarrow = QtWidgets.QRadioButton("x-out")
        self.rbtn_sett_nodisparrow = QtWidgets.QRadioButton("Don't show")
        self.edt_sett_plttitle = QtWidgets.QLineEdit()

        # push buttons
        self.btn_plot = QtWidgets.QPushButton("Plot")
        self.btn_load_conf = QtWidgets.QPushButton("Load Config")
        self.btn_save_conf = QtWidgets.QPushButton("Save Config")
        self.btn_test = QtWidgets.QPushButton("Test")
        self.btn_about = QtWidgets.QPushButton("About")
        self.btn_quit = QtWidgets.QPushButton("Quit")

        # main widget
        self.mainwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainwidget)

        # style forms
        self.fontheader = QtGui.QFont()
        self.fontheader.setBold(True)

        # initialize the UI
        self.initUI()

        # set default values
        self.fill_default_values()

        # show the UI
        self.show()

    def initUI(self):
        """
        Initialize the UI
        """
        # bottom most row:
        bottomrowindex = 12  # depends on how many settings entries there are!
        if self.numberofsteps + 2 > bottomrowindex:
            bottomrowindex = self.numberofsteps + 2

        # define the grid layout
        layout = QtWidgets.QGridLayout()  # columns

        # ### column 1: labels for states
        # radiobuttons for nm or cm-1
        self.rbtngrp_units.addButton(self.rbtn_nm)
        self.rbtngrp_units.addButton(self.rbtn_cm)
        # set default
        self.rbtn_nm.setChecked(True)
        cmlabel = QtWidgets.QLabel("cm<sup>-1</sup>")
        self.rbtn_nm.setToolTip("Enter steps of laser scheme in nm")
        self.rbtn_cm.setToolTip("Enter steps of laser scheme in cm<sup>-1</sup>.")
        cmlabel.setToolTip("Enter steps of laser scheme in cm<sup>-1</sup>.")
        # add to layout
        rbtn_layout = QtWidgets.QHBoxLayout()
        rbtn_layout.addWidget(self.rbtn_nm)
        rbtn_layout.addStretch()
        rbtn_layout.addWidget(self.rbtn_cm)
        # this is a workaround, since the Radiobutton cannot accept a rich text label. It works
        rbtn_layout.addWidget(cmlabel)
        layout.addLayout(rbtn_layout, 0, 0, 1, 1)

        # headers for all
        # level
        lbl_level = QtWidgets.QLabel("Level")
        lbl_level.setFont(self.fontheader)
        layout.addWidget(lbl_level, 0, 1, 1, 1)
        # term symbol
        lbl_trmsymb = QtWidgets.QLabel("Term Symbol")
        lbl_trmsymb.setFont(self.fontheader)
        layout.addWidget(lbl_trmsymb, 0, 2, 1, 1)
        # ground state manifold?
        lbl_gsmani = QtWidgets.QLabel("GS Manifold?")
        lbl_gsmani.setFont(self.fontheader)
        layout.addWidget(lbl_gsmani, 0, 3, 1, 1)
        # Forbidden transition
        lbl_forbidden = QtWidgets.QLabel("Forbidden?")
        lbl_forbidden.setFont(self.fontheader)
        layout.addWidget(lbl_forbidden, 0, 4, 1, 1)
        # Settings
        lbl_sett = QtWidgets.QLabel("Settings")
        lbl_sett.setFont(self.fontheader)
        layout.addWidget(lbl_sett, 0, 5, 1, 1)
        # plot title
        lbl_plttit = QtWidgets.QLabel("Plot Title")
        lbl_plttit.setFont(self.fontheader)
        layout.addWidget(lbl_plttit, 0, 7, 1, 1)

        # ground state
        lbl_gs = QtWidgets.QLabel("Ground state (cm<sup>-1</sup>)")
        layout.addWidget(lbl_gs, 1, 0, 1, 1)
        layout.addWidget(self.edt_gslevel, 1, 1, 1, 1)
        layout.addWidget(self.edt_gsterm, 1, 2, 1, 1)
        self.edt_gslevel.setToolTip("Set the ground state level in cm<sup>-1</sup>.")
        tt_termsymbol = (
            "For example, 2P3 for <sup>2</sup>P<sub>3</sub>. If only J-state is "
            "known, you "
            "can also enter something like 'J=3'."
        )
        self.edt_gsterm.setToolTip(
            "Set the term symbol for the ground state. " + tt_termsymbol
        )

        # individual steps
        for it in range(self.numberofsteps):
            # make label and append
            self.lbl_steps.append(QtWidgets.QLabel())
            layout.addWidget(self.lbl_steps[it], 2 + it, 0, 1, 1)
            # level steps
            self.edt_level.append(QtWidgets.QLineEdit())
            self.edt_level[it].setFixedSize(self.lineedit_size)
            self.edt_level[it].setValidator(QtGui.QDoubleValidator())
            self.edt_level[it].setAlignment(QtCore.Qt.AlignRight)
            self.edt_level[it].setToolTip(
                "Enter the level of the given step in the selected unit."
            )
            layout.addWidget(self.edt_level[it], 2 + it, 1, 1, 1)
            # term symbol steps
            self.edt_term.append(QtWidgets.QLineEdit())
            self.edt_term[it].setFixedSize(self.lineedit_size)
            self.edt_term[it].setToolTip(
                "Enter term symbol for selected step. " + tt_termsymbol
            )
            layout.addWidget(self.edt_term[it], 2 + it, 2, 1, 1)
            # check boxes
            self.chk_lowlying.append(QtWidgets.QCheckBox("Low-lying state?"))
            layout.addWidget(self.chk_lowlying[it], 2 + it, 3, 1, 1)
            self.chk_lowlying[it].toggled.connect(self.set_label_names)
            self.chk_lowlying[it].setToolTip("Check if this is a low-lying state?")
            # forbidden transition
            self.chk_forbidden.append(QtWidgets.QCheckBox())
            tmplayout = QtWidgets.QHBoxLayout()
            tmplayout.addStretch()
            tmplayout.addWidget(self.chk_forbidden[it])
            tmplayout.addStretch()
            layout.addLayout(tmplayout, 2 + it, 4, 1, 1)
            self.chk_forbidden[it].setToolTip(
                "Check this box to mark the\n" "transition as forbidden."
            )

        # name the labels
        self.set_label_names()

        # add IP label:
        ip_lbl = QtWidgets.QLabel("IP (cm<sup>-1</sup>)")
        layout.addWidget(ip_lbl, 2 + len(self.lbl_steps), 0, 1, 1)
        layout.addWidget(self.edt_iplevel, 2 + len(self.lbl_steps), 1, 1, 1)
        layout.addWidget(self.edt_ipterm, 2 + len(self.lbl_steps), 2, 1, 1)
        self.edt_iplevel.setToolTip("Set IP level in cm<sup>-1</sup>.")
        self.edt_ipterm.setToolTip("Set term symbol of IP. " + tt_termsymbol)

        # set sizes and validators of boxes defined outside loop
        self.edt_gslevel.setFixedSize(self.lineedit_size)
        self.edt_gslevel.setValidator(QtGui.QDoubleValidator())
        self.edt_gslevel.setAlignment(QtCore.Qt.AlignRight)
        self.edt_gsterm.setFixedSize(self.lineedit_size)
        self.edt_iplevel.setFixedSize(self.lineedit_size)
        self.edt_iplevel.setValidator(QtGui.QDoubleValidator())
        self.edt_iplevel.setAlignment(QtCore.Qt.AlignRight)
        self.edt_ipterm.setFixedSize(self.lineedit_size)

        # button group for ip label
        self.rbtngrp_iplabel.addButton(self.rbtn_iplable_top)
        self.rbtngrp_iplabel.addButton(self.rbtn_iplable_bottom)

        # button group for how to display forbidden transitions
        self.rbtngrp_sett_forbidden.addButton(self.rbtn_sett_xoutarrow)
        self.rbtngrp_sett_forbidden.addButton(self.rbtn_sett_nodisparrow)

        # labels for settings
        layout.addWidget(QtWidgets.QLabel("Figure Width x Height:"), 1, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size title:"), 2, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size axes:"), 3, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size axes label:"), 4, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size labels:"), 5, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Headspace (cm<sup>-1</sup>):"), 6, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Arrow width:"), 7, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Arrow head width:"), 8, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Precision wavelength:"), 9, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Precision level:"), 10, 5, 1, 1)
        layout.addWidget(QtWidgets.QLabel("IP label position:"), 11, 5, 1, 1)
        layout.addWidget(
            QtWidgets.QLabel("Display forbidden transitions:"), 12, 5, 1, 1
        )
        # line edits and buttons, include tooltips
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.edt_sett_figwidth)
        self.edt_sett_figwidth.setToolTip("Width of figure in inches.")
        tmplayout.addStretch()
        tmplayout.addWidget(QtWidgets.QLabel("x"))
        tmplayout.addStretch()
        tmplayout.addWidget(self.edt_sett_figheight)
        self.edt_sett_figheight.setToolTip("Height of figure in inches.")
        layout.addLayout(tmplayout, 1, 6, 1, 1)
        layout.addWidget(self.edt_sett_fstitle, 2, 6, 1, 1)
        self.edt_sett_fstitle.setToolTip("Font size of the plot title.")
        layout.addWidget(self.edt_sett_fsaxes, 3, 6, 1, 1)
        self.edt_sett_fsaxes.setToolTip("Font size of axes ticks.")
        layout.addWidget(self.edt_sett_fsaxlbl, 4, 6, 1, 1)
        self.edt_sett_fsaxlbl.setToolTip("Font size of axes labels.")
        # line breaks
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_linebreaks)
        tmplayout.addStretch()
        layout.addLayout(tmplayout, 4, 7, 1, 1)
        self.chk_sett_linebreaks.setToolTip(
            "Should there be a line break between\n"
            "the state and the term symbol? Play\n"
            "with this to make the the plot look nicer."
        )
        layout.addWidget(self.edt_sett_fslbl, 5, 6, 1, 1)
        # check box show cm-1 axis
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_showcmax)
        tmplayout.addStretch()
        tmplabel = QtWidgets.QLabel("Show cm-1 axis labels?")
        tmplayout.addWidget(tmplabel)
        layout.addLayout(tmplayout, 5, 7, 1, 1)
        self.chk_sett_showcmax.setToolTip(
            "Show the cm<sup>-1</sup> (left) axis? You can turn this off in case you "
            "want to stich plots together afterwards! This function will also hide the "
            "ticks."
        )
        tmplabel.setToolTip(
            "Show the cm<sup>-1</sup> (left) axis? You can turn this off in case you "
            "want to stich plots together afterwards! This function will also hide the "
            "ticks."
        )
        self.edt_sett_fslbl.setToolTip("Font size of the labels.")
        layout.addWidget(self.edt_sett_headspace, 6, 6, 1, 1)
        # check box show eV axis
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_showevax)
        tmplayout.addStretch()
        layout.addLayout(tmplayout, 6, 7, 1, 1)
        self.chk_sett_showevax.setToolTip(
            "Show the eV (right) axis? You can turn this\n"
            " off in case you want to stich plots together\n"
            "afterwards! This function will also hide the\n"
            "ticks."
        )
        self.edt_sett_headspace.setToolTip(
            "Set how much space is added on top of the"
            "IP level: the head space. Adjust this"
            "value whenever there is not enough space"
            "on top to fit all the text in. The value"
            "is given in cm<sup>-1</sup>."
        )
        layout.addWidget(self.edt_sett_arrwidth, 7, 6, 1, 1)
        self.edt_sett_arrwidth.setToolTip(
            "Set the width of the arrow line in\n"
            "undefine dunits. Play to get the ideal\n"
            "settings."
        )
        layout.addWidget(self.edt_sett_arrheadwidth, 8, 6, 1, 1)
        self.edt_sett_arrheadwidth.setToolTip(
            "Set the width of the arrwo head in\n"
            "undefined units. Play to get the ideal\n"
            "settings."
        )
        layout.addWidget(self.edt_sett_preclambda, 9, 6, 1, 1)
        self.edt_sett_preclambda.setToolTip(
            "Set the precision with which the wavelength\n" "is displayed on the plot."
        )
        layout.addWidget(self.edt_sett_preclevel, 10, 6, 1, 1)
        self.edt_sett_preclevel.setToolTip(
            "Set the precision with which the wavenumber\n" "is displayed on the plot."
        )
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.rbtn_iplable_top)
        self.rbtn_iplable_top.setChecked(True)  # set top as default
        tmplayout.addStretch()
        tmplayout.addWidget(self.rbtn_iplable_bottom)
        self.rbtn_iplable_top.setToolTip("Display the IP label above the line.")
        self.rbtn_iplable_bottom.setToolTip("Display the IP label below the line.")
        layout.addLayout(tmplayout, 11, 6, 1, 1)
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.rbtn_sett_xoutarrow)
        self.rbtn_sett_xoutarrow.setChecked(True)  # set top as default
        tmplayout.addStretch()
        tmplayout.addWidget(self.rbtn_sett_nodisparrow)
        self.rbtn_sett_xoutarrow.setToolTip(
            "Show an arrow for forbidden transitions\n" "but cross it out."
        )
        self.rbtn_sett_nodisparrow.setToolTip(
            "Don't show arrows for forbidden\n" "transitions."
        )
        layout.addLayout(tmplayout, 12, 6, 1, 1)
        layout.addWidget(self.edt_sett_plttitle, 1, 7, 1, 1)
        self.edt_sett_plttitle.setToolTip("Title of the plot.")

        # set sizes
        self.edt_sett_plttitle.setFixedSize(self.lineedit_size)
        # validators
        self.edt_sett_figwidth.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_figheight.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_fstitle.setValidator(QtGui.QIntValidator())
        self.edt_sett_fsaxes.setValidator(QtGui.QIntValidator())
        self.edt_sett_fsaxlbl.setValidator(QtGui.QIntValidator())
        self.edt_sett_fslbl.setValidator(QtGui.QIntValidator())
        self.edt_sett_headspace.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_arrwidth.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_arrheadwidth.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_preclambda.setValidator(QtGui.QIntValidator())
        self.edt_sett_preclevel.setValidator(QtGui.QIntValidator())
        # alignment
        self.edt_sett_figwidth.setAlignment(QtCore.Qt.AlignCenter)
        self.edt_sett_figheight.setAlignment(QtCore.Qt.AlignCenter)
        self.edt_sett_fstitle.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_fsaxes.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_fsaxlbl.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_fslbl.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_headspace.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_arrwidth.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_arrheadwidth.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_preclambda.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_preclevel.setAlignment(QtCore.Qt.AlignRight)

        # push buttons
        layout.addWidget(self.btn_plot, 2, 7, 1, 1)
        if self.rundebug:
            layout.addWidget(self.btn_test, bottomrowindex - 4, 7, 1, 1)
        layout.addWidget(self.btn_load_conf, bottomrowindex - 3, 7, 1, 1)
        layout.addWidget(self.btn_save_conf, bottomrowindex - 2, 7, 1, 1)
        layout.addWidget(self.btn_about, bottomrowindex - 1, 7, 1, 1)
        layout.addWidget(self.btn_quit, bottomrowindex, 7, 1, 1)

        # connect it all up
        self.rbtn_nm.toggled.connect(self.set_label_names)
        self.rbtn_cm.toggled.connect(self.set_label_names)
        # buttons
        self.btn_plot.clicked.connect(self.plot)
        self.btn_plot.setToolTip("Plot the scheme.")
        self.btn_load_conf.clicked.connect(self.load_config)
        self.btn_load_conf.setToolTip("Load a saved configuration file.")
        self.btn_save_conf.clicked.connect(self.save_config)
        self.btn_save_conf.setToolTip("Save the current configuration in a file.")
        self.btn_test.clicked.connect(self.test)
        self.btn_test.setToolTip(
            "This button should not be visible. If it is\n"
            "visible, it means that the\n"
            "self.rundebug\n"
            "value in the software is set to True. This\n"
            "is only meant for debugging and could have\n"
            "weird effects when using the software."
        )
        self.btn_about.clicked.connect(self.about)
        self.btn_about.setToolTip("Displays an about page with info on the program")
        self.btn_quit.clicked.connect(self.close)
        self.btn_quit.setToolTip("Close the program")

        # set the layout to the widget
        self.mainwidget.setLayout(layout)

    def fill_default_values(self):
        """
        Routine to fill default values in check boxes if they are empty.
        This is such that the user can't leave required fields empty
        """

        def fillme(field, value):
            """
            Fills values of line edits, if currently empty
            """
            if field.text() == "":
                field.setText(value)

        # loop through line edits
        fillme(
            self.edt_sett_figwidth, str(ut.DEFAULT_SETTINGS["settings"]["fig_width"])
        )
        fillme(
            self.edt_sett_figheight,
            str(ut.DEFAULT_SETTINGS["settings"]["fig_height"]),
        )
        fillme(self.edt_sett_fstitle, str(ut.DEFAULT_SETTINGS["settings"]["fs_title"]))
        fillme(self.edt_sett_fsaxes, str(ut.DEFAULT_SETTINGS["settings"]["fs_axes"]))
        fillme(self.edt_sett_fslbl, str(ut.DEFAULT_SETTINGS["settings"]["fs_labels"]))
        fillme(
            self.edt_sett_fsaxlbl,
            str(ut.DEFAULT_SETTINGS["settings"]["fs_axes_labels"]),
        )
        fillme(
            self.edt_sett_headspace,
            str(ut.DEFAULT_SETTINGS["settings"]["headspace"]),
        )
        fillme(
            self.edt_sett_arrwidth,
            str(ut.DEFAULT_SETTINGS["settings"]["arrow_width"]),
        )
        fillme(
            self.edt_sett_arrheadwidth,
            str(ut.DEFAULT_SETTINGS["settings"]["arrow_head_width"]),
        )
        fillme(
            self.edt_sett_preclambda,
            str(ut.DEFAULT_SETTINGS["settings"]["prec_wavelength"]),
        )
        fillme(
            self.edt_sett_preclevel,
            str(ut.DEFAULT_SETTINGS["settings"]["prec_level"]),
        )

    def set_label_names(self):
        # get the unit
        unit = self.get_unit()
        # set the labels
        stepnumb = 0
        for it in range(self.numberofsteps):
            stepnumb += 1
            # appendix for step number in label
            app = "th"
            if stepnumb == 1:
                app = "st"
            elif stepnumb == 2:
                app = "nd"
            elif stepnumb == 3:
                app = "rd"
            # set the namestring according to if low-lying is toggled or not
            if self.chk_lowlying[it].isChecked():
                stepnumb -= 1
                namestring = "Low lying st (cm<sup>-1</sup>)"
            else:
                namestring = str(stepnumb) + app + " step " + "(" + unit + "):"
            self.lbl_steps[it].setText(namestring)

    def get_unit(self):
        """
        Returns the current unit
        :return unit:   <str>   'nm' or 'cm<sup>-1</sup>'
        """
        if self.rbtn_nm.isChecked():
            return "nm"
        else:
            return "cm<sup>-1</sup>"

    def check_fields(self):
        """
        Check if the required fields are filled in.
        """
        # throw an error if not at least one box is filled
        if self.edt_level[0].text() == "":
            QtWidgets.QMessageBox.warning(
                self,
                "No entries",
                "Need at least one level to make a plot!",
                QtWidgets.QMessageBox.Ok,
            )
            return False

        # ip value
        try:
            _ = float(self.edt_iplevel.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self,
                "Enter IP",
                "Please enter an ionization potential as a number and try again.",
                QtWidgets.QMessageBox.Ok,
            )
            return False
        return True

    # buttons
    def plot(self):
        """
        Call the plotting window
        """
        if self.rundebug:
            print("Plotting...")
        if not self.check_fields():
            return

        # fill default values - if not already there
        self.fill_default_values()

        # open the plotting window
        data = self.write_json()

        PlotDisplay(data, parent=self)

    def load_config(self, **kwargs):
        """
        Load a configuration file that has previously been saved

        :param kwargs:  <dict>  Dictionary with additional keyword arguments
            - fname: <Path>  Path to the file to load
        """
        filename = kwargs.get("fname", None)

        if filename is None:
            options = QtWidgets.QFileDialog.Options()
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "QtWidgets.QFileDialog.getOpenFileName()",
                str(self.user_path.absolute()),
                filter="JSON Files (*.json);;All Files (*.*)",
                options=options,
            )
            # user pressed cancel
            if filename == "":
                return

            filename = Path(filename)

        self.user_path = filename.parent
        # load the json file
        savedict = ut.json_reader(filename)

        # function for setting line edits
        def set_line_edits(category, entry, lineedit):
            """
            Sets a given line edit from the dictionary, but also checks if available.
            :param category:    <string>    Category the entry is in
            :param entry:       <string>    Entry with the value
            :param lineedit:    <QtWidgets.QLineEdit> The object for the text
            """
            try:
                lineedit.setText(savedict[category][entry])
            except KeyError:
                pass

        # set the settings for the levels
        try:
            if savedict["scheme"]["unit"] == "nm":
                self.rbtn_nm.setChecked(True)
            else:
                self.rbtn_cm.setChecked(True)
        except KeyError:
            pass

        set_line_edits("scheme", "gs_level", self.edt_gslevel)
        set_line_edits("scheme", "gs_term", self.edt_gsterm)
        for it in range(
            len(self.edt_level)
        ):  # only loop through as many entries as there are
            set_line_edits("scheme", "step_level" + str(it), self.edt_level[it])
            set_line_edits("scheme", "step_term" + str(it), self.edt_term[it])
            try:
                if savedict["scheme"]["step_lowlying" + str(it)]:
                    self.chk_lowlying[it].setChecked(True)
                else:
                    self.chk_lowlying[it].setChecked(False)
            except KeyError:
                self.chk_lowlying[it].setChecked(False)
            try:
                if savedict["scheme"]["step_forbidden" + str(it)]:
                    self.chk_forbidden[it].setChecked(True)
                else:
                    self.chk_forbidden[it].setChecked(False)
            except KeyError:
                self.chk_forbidden[it].setChecked(False)
        set_line_edits("scheme", "ip_level", self.edt_iplevel)
        set_line_edits("scheme", "ip_term", self.edt_ipterm)

        # program settings - alphabetically
        set_line_edits("settings", "arrow_head_width", self.edt_sett_arrheadwidth)
        set_line_edits("settings", "arrow_width", self.edt_sett_arrwidth)
        set_line_edits("settings", "fig_height", self.edt_sett_figheight)
        set_line_edits("settings", "fig_width", self.edt_sett_figwidth)
        set_line_edits("settings", "fs_axes", self.edt_sett_fsaxes)
        set_line_edits("settings", "fs_axes_labels", self.edt_sett_fsaxlbl)
        set_line_edits("settings", "fs_labels", self.edt_sett_fslbl)
        set_line_edits("settings", "fs_title", self.edt_sett_fstitle)
        set_line_edits("settings", "headspace", self.edt_sett_headspace)
        try:
            if savedict["settings"]["ip_label_pos"] == "Top":
                self.rbtn_iplable_top.setChecked(True)
            else:
                self.rbtn_iplable_bottom.setChecked(True)
        except KeyError:
            self.rbtn_iplable_bottom.setChecked(True)
        # how to display forbidden transitions
        try:
            if savedict["settings"]["show_forbidden_transitions"] == "x-out":
                self.rbtn_sett_xoutarrow.setChecked(True)
            else:
                self.rbtn_sett_nodisparrow.setChecked(True)
        except KeyError:
            self.rbtn_sett_xoutarrow.setChecked(True)
        # line breaks
        try:
            if savedict["settings"]["line_breaks"]:
                self.chk_sett_linebreaks.setChecked(True)
            else:
                self.chk_sett_linebreaks.setChecked(False)
        except KeyError:
            self.chk_sett_linebreaks.setChecked(True)
        # show cm-1 axis
        try:
            if savedict["settings"]["show_cm-1_axis"]:
                self.chk_sett_showcmax.setChecked(True)
            else:
                self.chk_sett_showcmax.setChecked(False)
        except KeyError:
            self.chk_sett_showcmax.setChecked(True)
        # show eV axis
        try:
            if savedict["settings"]["show_eV_axis"]:
                self.chk_sett_showevax.setChecked(True)
            else:
                self.chk_sett_showevax.setChecked(False)
        except KeyError:
            self.chk_sett_showevax.setChecked(True)

        set_line_edits("settings", "plot_title", self.edt_sett_plttitle)
        set_line_edits("settings", "prec_level", self.edt_sett_preclevel)
        set_line_edits("settings", "prec_wavelength", self.edt_sett_preclambda)

    def write_json(self) -> dict:
        """Write the json dictionary to save or pass on.

        :return: JSON dictionary that can either be directly plotted or can be saved.
        """
        # create the dictionary to save
        savedict = {}
        savedict["scheme"] = {}
        savedict["settings"] = {}

        # save the levels
        savedict["scheme"]["unit"] = self.get_unit()
        savedict["scheme"]["gs_level"] = self.edt_gslevel.text()
        savedict["scheme"]["gs_term"] = self.edt_gsterm.text()
        for it in range(len(self.lbl_steps)):
            savedict["scheme"]["step_level" + str(it)] = self.edt_level[it].text()
            savedict["scheme"]["step_term" + str(it)] = self.edt_term[it].text()
            savedict["scheme"]["step_lowlying" + str(it)] = self.chk_lowlying[
                it
            ].isChecked()
            savedict["scheme"]["step_forbidden" + str(it)] = self.chk_forbidden[
                it
            ].isChecked()
        savedict["scheme"]["ip_level"] = self.edt_iplevel.text()
        savedict["scheme"]["ip_term"] = self.edt_ipterm.text()

        # save the settings
        savedict["settings"]["fig_width"] = self.edt_sett_figwidth.text()
        savedict["settings"]["fig_height"] = self.edt_sett_figheight.text()
        savedict["settings"]["fs_title"] = self.edt_sett_fstitle.text()
        savedict["settings"]["fs_axes"] = self.edt_sett_fsaxes.text()
        savedict["settings"]["fs_axes_labels"] = self.edt_sett_fsaxlbl.text()
        savedict["settings"]["fs_labels"] = self.edt_sett_fslbl.text()
        savedict["settings"]["headspace"] = self.edt_sett_headspace.text()
        savedict["settings"]["arrow_width"] = self.edt_sett_arrwidth.text()
        savedict["settings"]["arrow_head_width"] = self.edt_sett_arrheadwidth.text()
        savedict["settings"]["prec_wavelength"] = self.edt_sett_preclambda.text()
        savedict["settings"]["prec_level"] = self.edt_sett_preclevel.text()
        if self.rbtn_iplable_top.isChecked():
            iptablepos = "Top"
        else:
            iptablepos = "Bottom"
        savedict["settings"]["ip_label_pos"] = iptablepos
        if self.rbtn_sett_xoutarrow.isChecked():
            dispforbidden = "x-out"
        else:
            dispforbidden = "noshow"
        savedict["settings"]["show_forbidden_transitions"] = dispforbidden
        savedict["settings"]["plot_title"] = self.edt_sett_plttitle.text()
        savedict["settings"]["line_breaks"] = self.chk_sett_linebreaks.isChecked()
        savedict["settings"]["show_cm-1_axis"] = self.chk_sett_showcmax.isChecked()
        savedict["settings"]["show_eV_axis"] = self.chk_sett_showevax.isChecked()

        return savedict

    def save_config(self):
        """
        Save the current configuration as a .json file the user defines
        """
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "QtWidgets.QFileDialog.getOpenFileName()",
            str(self.user_path.absolute()),
            filter="JSON Files (*.json);;All Files (*.*)",
            options=options,
        )
        # user pressed cancel
        if filename == "":
            return

        filename = Path(filename)
        self.user_path = filename.parent

        savedict = self.write_json()

        with open(filename, "w") as write_file:
            json.dump(savedict, write_file, indent=4, sort_keys=True)

    def about(self):
        """
        Gives a QtWidgets.QMessageBox with an about thing
        :return:
        """
        about_msg = (
            "<center>"
            "<h1>RIMS Scheme drawer</h1>"
            "<br>Version: "
            + self.version
            + "<p>Author: "
            + self.author
            + "<p>Please see the github repository for bug reports, feature requests, "
            "and for contacting the"
            "author."
            "<p>Many tooltips are implemented that can help you with the software. "
            "Hover over entries"
            "with the mouse and check those tooltips out."
        )
        QtWidgets.QMessageBox.about(self, "About", about_msg)

    def test(self):
        """
        Development testing routine, with the according button
        """
        fname = Path.home().joinpath(
            "Documents/code/RIMSCode/RIMSSchemeDrawer/examples/example_titanium.json"
        )
        self.load_config(fname=fname)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        super().__init__()
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class PlotDisplay(QtWidgets.QMainWindow):
    def __init__(self, json_data: dict, parent: QtWidgets.QWidget = None):
        super(PlotDisplay, self).__init__(parent=parent)

        sc = MplCanvas(width=5, height=4, dpi=100)
        Plotter(json_data, fig_ax=(sc.figure, sc.axes))

        toolbar = NavigationToolbar(sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()
