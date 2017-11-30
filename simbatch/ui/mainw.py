import ctypes

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:
    print "PySide.QtCore ERR"

from ui_wizard import WizardUI
from ui_projects import ProjectsUI
from ui_schemas import SchemasUI
from ui_settings import SettingsUI


class TopMenuUI:
    qt_lay_top_menu = None
    instance = None
    batch = None

    qt_but_debug = None
    qt_but_filter = None
    qt_but_refresh = None
    qt_but_print_general = None
    qt_but_print_details = None

    current_top_info_mode = 1

    def __init__(self, layout, instance, batch):
        self.batch = batch
        qt_lay_top_menu = QHBoxLayout()
        self.qt_lay_top_menu = qt_lay_top_menu
        self.instance = instance
        layout.addLayout(qt_lay_top_menu)

        qt_lbl_info = QLabel("info")
        qt_font = QFont()
        qt_font.setPointSize(10)
        qt_font.setBold(True)
        qt_font.setFamily("Veranda")
        qt_lbl_info.setFont(qt_font)
        self.qt_lbl_info = qt_lbl_info
        qt_lbl_info.setStyleSheet("""border: 0px solid white;padding-left:7px;""")
        qt_lay_top_menu.addWidget(qt_lbl_info)

        qt_lay_top_menu.addStretch(1)

        qt_but_print_general = QPushButton("[i]")
        qt_but_print_general.setMinimumSize(22, 22)
        qt_but_print_general.setMaximumSize(22, 22)
        qt_lay_top_menu.addWidget(qt_but_print_general)
        self.qt_but_print_general = qt_but_print_general

        qt_but_print_details = QPushButton("[ii]")
        qt_but_print_details.setMinimumSize(22, 22)
        qt_but_print_details.setMaximumSize(22, 22)
        qt_lay_top_menu.addWidget(qt_but_print_details)
        self.qt_but_print_details = qt_but_print_details

        qt_but_debug = QPushButton("[db]")
        qt_but_debug.setMinimumSize(22, 22)
        qt_but_debug.setMaximumSize(22, 22)
        qt_lay_top_menu.addWidget(qt_but_debug)
        self.qt_but_debug = qt_but_debug

        qt_but_filter = QPushButton("F")
        qt_but_filter.setMinimumSize(22, 22)
        qt_but_filter.setMaximumSize(22, 22)
        qt_lay_top_menu.addWidget(qt_but_filter)
        self.qt_but_filter = qt_but_filter

        qt_but_refresh = QPushButton("R")
        qt_but_refresh.setMinimumSize(22, 22)
        qt_but_refresh.setMaximumSize(22, 22)
        qt_lay_top_menu.addWidget(qt_but_refresh)
        self.qt_but_refresh = qt_but_refresh

    def set_top_info(self, txt, mode=1, limit=0):  # 1 normal ...  9 error
        if mode > 1:
            txt = "     " + txt + "          "
        if limit > 0:
            if len(txt) > limit:
                txt = txt[:limit] + "  ..."
        self.qt_lbl_info.setText(txt)
        if self.current_top_info_mode != mode:
            if self.batch.s.currentSoft == 2:
                if mode == 1:
                    self.qt_lbl_info.setStyleSheet("")
                if mode == 7:
                    self.qt_lbl_info.setStyleSheet("""color:#000000;background-color:#ffdc1a;""")
                if mode == 8:
                    self.qt_lbl_info.setStyleSheet("""color:#000000;background-color:#ffa722;""")
                if mode == 9:
                    self.qt_lbl_info.setStyleSheet("""color:#000000;background-color:#ff4422;""")
            else:
                if mode == 1:
                    self.qt_lbl_info.setStyleSheet("")
                if mode == 7:
                    self.qt_lbl_info.setStyleSheet("""background-color:#f2dc1a;""")
                if mode == 8:
                    self.qt_lbl_info.setStyleSheet("""background-color:#ffa722;""")
                if mode == 9:
                    self.qt_lbl_info.setStyleSheet("""background-color:#ff4422;""")
        self.current_top_info_mode = mode


class MainWindow(QMainWindow):
    sim_batch = None
    comfun = None
    debug_level = None

    top_ui = None
    wiz_ui = None
    pro_ui = None
    sch_ui = None
    tsk_ui = None
    que_ui = None
    nod_ui = None
    set_ui = None

    qt_tab_widget = None

    def __init__(self, sim_batch, parent=None):
        super(MainWindow, self).__init__(parent)
        self.sim_batch = sim_batch
        self.comfun = sim_batch.comfun
        self.s = sim_batch.s
        self.init_ui(sim_batch)
        self.debug_level = sim_batch.s.debug_level

    def init_ui(self, batch):
        user32 = ctypes.windll.user32
        wnd = self.s.window
        current_screen_width = user32.GetSystemMetrics(0)
        current_screen_height = user32.GetSystemMetrics(1)

        if len(wnd) == 4:
            x_wnd_pos = wnd[0]
            y_wnd_pos = wnd[1]

            if self.s.CHECK_SCREEN_RES_ON_START == 1:
                if wnd[0] > current_screen_width - 130:
                    x_wnd_pos = 40
                    if self.debug_level >= 3:
                        print "  [INF] reset window position X "
                if wnd[1] > current_screen_height - 130:
                    y_wnd_pos = 40
                    if self.debug_level >= 3:
                        print "  [INF] reset window position Y "
            else:
                x_wnd_pos = wnd[0]
                y_wnd_pos = wnd[1]
            if self.debug_level >= 3:
                print "  [INF] set wind pos : ",  x_wnd_pos, y_wnd_pos,  wnd[2],  wnd[3]
            self.setGeometry(x_wnd_pos, y_wnd_pos, wnd[2], wnd[3])

        self.setWindowTitle("SimBatch " + self.s.SIMBATCH_VERSION + "       " + self.s.current_soft_name)
        qt_central_widget = QWidget(self)
        self.setCentralWidget(qt_central_widget)
        qt_lay_central = QVBoxLayout(qt_central_widget)
        qt_lay_central.setContentsMargins(0, 0, 0, 0)

        top = TopMenuUI(qt_lay_central, self, batch)
        top.qt_but_print_general.clicked.connect(self.on_clicked_but_print_general)
        top.qt_but_print_details.clicked.connect(self.on_clicked_but_print_details)
        top.qt_but_debug.clicked.connect(self.on_clicked_but_debug)
        top.qt_but_filter.clicked.connect(self.on_clicked_but_filter)
        top.qt_but_refresh.clicked.connect(self.on_clicked_but_refresh)

        self.top_ui = top
        self.wiz_ui = WizardUI(batch, top)
        self.pro_ui = ProjectsUI(batch, top)
        self.sch_ui = SchemasUI(batch, top)
        #  self.tsk_ui = TasksUI(batch)
        #  self.que_ui = QueueUI(batch)
        #  self.nod_ui = NodesUI(batch)

        self.set_ui = SettingsUI(batch, top)

        #  TABs
        #  TABs   TABs
        #  TABs   TABs   TABs
        qt_tab_widget = QTabWidget(self)
        self.qt_tab_widget = qt_tab_widget

        qt_tab_widget.addTab(self.wiz_ui.qt_widget_wizard, "Wizard")
        qt_tab_widget.addTab(self.pro_ui.qt_widget_projects, "Projects")
        qt_tab_widget.addTab(self.sch_ui.qt_widget_schema, "Schemas")
        #  qt_tab_widget.addTab(tsk.widgetTasks, "Tasks")
        #  qt_tab_widget.addTab(que.widgetQueue, "Queue")
        #  qt_tab_widget.addTab(nod.widgetNodes, "Sim Nodes")
        qt_tab_widget.addTab(self.set_ui.qt_widget_settings, "Settings")
        qt_tab_widget.setMinimumSize(220, 400)

        if self.s.loading_state < 10:
            qt_tab_widget.setCurrentIndex(1)    # show settings
        else:
            qt_tab_widget.setCurrentIndex(1)    # show tasks

        qt_lay_central.addWidget(qt_tab_widget)
        qt_central_widget.setLayout(qt_lay_central)
        qt_tab_widget.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, tab):  # TODO
        if self.s.debug_level >= 3:
            print tab

    def init_lists(self):
        if self.s.debug_level >= 3:
            print " [INF] init lists"

    def on_clicked_but_print_general(self):
        self.sim_batch.print_important_values()

    def on_clicked_but_print_details(self):
        self.sim_batch.print_current_module_values(self.qt_tab_widget.currentIndex())  # valid for: P S T Q N

    def on_clicked_but_debug(self):
        if self.s.debug_level >= 3:
            print " [INF] but_debug"

    def on_clicked_but_filter(self):
        if self.s.debug_level >= 3:
            print " [INF] filter"

    def on_clicked_but_refresh(self):
        if self.s.debug_level >= 3:
            print " [INF] but_refresh"

    def resizeEvent(self, event):            # PySide  resizeEvent
        self.on_resize_window(event)

    def on_resize_window(self, event):
        newSize = event.size()
        self.s.window[2] = newSize.width()
        self.s.window[3] = newSize.height()

    def moveEvent(self, event):             # PySide  moveEvent
        self.on_move_window(event)

    def on_move_window(self, event):
        newPos = event.pos()
        self.s.window[0] = newPos.x()
        self.s.window[1] = newPos.y()


