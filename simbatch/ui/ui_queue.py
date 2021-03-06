# import copy
import subprocess

try:  # Maya 2016
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:
    try:  # Maya 2017
        from PySide2.QtCore import *
        from PySide2.QtGui import *
        from PySide2.QtWidgets import *
    except ImportError:
        raise Exception('PySide import ERROR!  Please install PySide or PySide2')

from widgets import *


class QueueListItem(QWidget):
    def __init__(self, txt_id, txt_name, txt_user, txt_prior, txt_state, txt_evo, txt_node, txt_desc):
        super(QueueListItem, self).__init__()
        self.qt_widget = QWidget(self)
        self.qt_label_font = QFont()
        self.qt_label_font.setPointSize(8)

        self.qt_lay = QHBoxLayout(self.qt_widget)
        self.qt_lay.setSpacing(0)
        self.qt_lay.setContentsMargins(0, 0, 0, 0)

        self.qt_label_id = QLabel(txt_id)
        self.qt_label_id.setFont(self.qt_label_font)
        self.qt_label_id.setStyleSheet("""color:#000;""")
        self.qt_label_id.setMinimumWidth(22)
        self.qt_label_id.setMaximumWidth(22)
        self.qt_lay.addWidget(self.qt_label_id)

        self.qt_label_name = QLabel(txt_name)
        self.qt_label_name.setFont(self.qt_label_font)
        self.qt_label_name.setStyleSheet("""color:#000;""")
        self.qt_label_name.setMinimumWidth(180)
        self.qt_label_name.setMaximumWidth(250)
        self.qt_lay.addWidget(self.qt_label_name)

        self.qt_label_user = QLabel(txt_user)
        self.qt_label_user.setFont(self.qt_label_font)
        self.qt_label_user.setStyleSheet("""color:#000;""")
        self.qt_label_user.setMinimumWidth(22)
        self.qt_label_user.setMaximumWidth(30)
        self.qt_lay.addWidget(self.qt_label_user)

        self.qt_label_prior = QLabel(txt_prior)
        self.qt_label_prior.setFont(self.qt_label_font)
        self.qt_label_prior.setStyleSheet("""color:#000;""")
        self.qt_label_prior.setMinimumWidth(22)
        self.qt_label_prior.setMaximumWidth(30)
        self.qt_lay.addWidget(self.qt_label_prior)

        self.qt_label_state = QLabel(txt_state)
        self.qt_label_state.setFont(self.qt_label_font)
        self.qt_label_state.setStyleSheet("""color:#000;""")
        self.qt_label_state.setMinimumWidth(55)
        self.qt_label_state.setMaximumWidth(70)
        self.qt_lay.addWidget(self.qt_label_state)

        self.qt_label_evo = QLabel(txt_evo)
        self.qt_label_evo.setFont(self.qt_label_font)
        self.qt_label_evo.setStyleSheet("""color:#000;""")
        self.qt_label_evo.setMinimumWidth(70)
        self.qt_label_evo.setMaximumWidth(170)
        self.qt_lay.addWidget(self.qt_label_evo)

        self.qt_label_node = QLabel(txt_node)
        self.qt_label_node.setFont(self.qt_label_font)
        self.qt_label_node.setStyleSheet("""color:#000;""")
        self.qt_lay.addWidget(self.qt_label_node)

        self.qt_label_desc = QLabel(txt_desc)
        self.qt_label_desc.setFont(self.qt_label_font)
        self.qt_label_desc.setStyleSheet("""color:#000;""")
        self.qt_lay.addWidget(self.qt_label_desc)

        self.setLayout(self.qt_lay)


class QueueUI:
    list_queue = None
    qt_widget_queue = None

    batch = None
    top_ui = None

    qt_form_edit = None
    qt_form_remove = None

    edit_form_state = 0
    remove_form_state = 0

    qt_edit_fe_name = None
    qt_edit_fe_pror = None
    qt_edit_fe_state = None
    qt_fe_description = None

    freeze_list_on_changed = 0

    array_visible_queue_items_ids = []

    current_list_item_index = None
    last_list_item_index = None

    def __init__(self, batch, mainw, top):
        self.batch = batch
        self.sts = batch.sts
        self.que = batch.que
        self.comfun = batch.comfun
        self.top_ui = top
        self.mainw = mainw

        list_queue = QListWidget()
        list_queue.setSelectionMode(QAbstractItemView.NoSelection)

        list_queue.setFrameShadow(QFrame.Raised)
        list_queue.currentItemChanged.connect(self.on_current_item_changed)
        list_queue.setSpacing(1)
        p = list_queue.sizePolicy()
        p.setVerticalPolicy(QSizePolicy.Policy.Maximum)

        list_queue.setContextMenuPolicy(Qt.CustomContextMenu)
        list_queue.customContextMenuRequested.connect(self.on_right_click_show_menu)

        self.list_queue = list_queue

        qt_widget_queue = QWidget()
        self.qt_widget_queue = qt_widget_queue
        qt_lay_queue_main = QVBoxLayout(qt_widget_queue)
        qt_lay_queue_main.setContentsMargins(0, 0, 0, 0)

        qt_lay_queue_list = QHBoxLayout()
        qt_lay_forms = QVBoxLayout()
        qt_lay_queue_buttons = QHBoxLayout()

        # EDIT
        # EDIT EDIT
        # EDIT EDIT EDIT
        qt_form_edit = QWidget()
        self.qt_form_edit = qt_form_edit
        qt_form_edit_layout_ext = QVBoxLayout()
        qt_form_edit.setLayout(qt_form_edit_layout_ext)

        qt_form_edit_layout = QVBoxLayout()

        # fe   form edit
        qt_edit_button_fe_name = EditLineWithButtons("Queue item name: ")
        qt_edit_button_fe_prior = EditLineWithButtons("Priority: ", label_minimum_size=65)
        qt_edit_button_fe_state = EditLineWithButtons("State: ", label_minimum_size=65)
        qt_edit_button_fe_descr = EditLineWithButtons("Description:  ", label_minimum_size=65)
        self.qt_edit_fe_name = qt_edit_button_fe_name.qt_edit_line
        self.qt_edit_fe_pror = qt_edit_button_fe_prior.qt_edit_line
        self.qt_edit_fe_state = qt_edit_button_fe_state.qt_edit_line
        self.qt_fe_description = qt_edit_button_fe_descr.qt_edit_line

        qt_cb_button_save = ButtonWithCheckBoxes("Save changes", pin_text="pin")
        qt_cb_button_save.button.clicked.connect(
            lambda: self.on_click_save_changes(qt_edit_button_fe_name.get_txt(), qt_edit_button_fe_prior.get_txt(),
                                               qt_edit_button_fe_state.get_txt(), qt_edit_button_fe_descr.get_txt()))

        qt_form_edit_layout.addLayout(qt_edit_button_fe_name.qt_widget_layout)
        qt_form_edit_layout.addLayout(qt_edit_button_fe_prior.qt_widget_layout)
        qt_form_edit_layout.addLayout(qt_edit_button_fe_state.qt_widget_layout)
        qt_form_edit_layout.addLayout(qt_edit_button_fe_descr.qt_widget_layout)
        qt_form_edit_layout.addLayout(qt_cb_button_save.qt_widget_layout)

        # TODO
        qt_gb_edit = QGroupBox()
        qt_gb_edit.setLayout(qt_form_edit_layout)
        qt_form_edit_layout_ext.addWidget(qt_gb_edit)

        # REMOVE
        # REMOVE REMOVE
        # REMOVE REMOVE REMOVE
        qt_form_remove = QWidget()
        self.qt_form_remove = qt_form_remove
        qt_form_remove_layout_ext = QVBoxLayout()
        qt_form_remove.setLayout(qt_form_remove_layout_ext)

        qt_form_remove_layout = QFormLayout()

        qt_cb_button_remove = ButtonWithCheckBoxes("Yes, remove", label_text="Remove selected ?        ")

        qt_form_remove_layout.addRow(" ", QLabel("   "))
        qt_form_remove_layout.addRow(" ", qt_cb_button_remove.qt_widget_layout)
        qt_form_remove_layout.addRow(" ", QLabel("   "))
        qt_cb_button_remove.button.clicked.connect(self.on_click_confirmed_remove_queue_item)

        qt_gb_remove = QGroupBox()
        qt_gb_remove.setLayout(qt_form_remove_layout)
        qt_form_remove_layout_ext.addWidget(qt_gb_remove)

        self.comfun.add_wigdets(qt_lay_forms, [qt_form_edit, qt_form_remove])

        self.hide_all_forms()

        qt_button_sim_one = QPushButton("Simulate One")
        qt_button_sim_all = QPushButton("Simulate All")
        qt_button_queue_edit = QPushButton("Edit")
        qt_button_queue_remove = QPushButton("Remove from Queue")

        qt_button_sim_one.clicked.connect(self.on_click_sim_one)
        qt_button_sim_all.clicked.connect(self.on_click_sim_all)
        qt_button_queue_edit.clicked.connect(self.on_click_edit)
        qt_button_queue_remove.clicked.connect(self.on_click_remove)

        qt_lay_queue_list.addWidget(list_queue)
        self.comfun.add_wigdets(qt_lay_queue_buttons,
                                [qt_button_sim_one, qt_button_sim_all, qt_button_queue_edit, qt_button_queue_remove])
        self.comfun.add_layouts(qt_lay_queue_main, [qt_lay_queue_list, qt_lay_forms, qt_lay_queue_buttons])

        self.init_queue_items()

    def init_queue_items(self):
        widget_list = self.list_queue
        qt_list_item = QListWidgetItem(widget_list)
        qt_list_item.setBackground(QBrush(QColor("#ddd")))
        qt_list_item.setFlags(Qt.ItemFlag.NoItemFlags)

        list_item_widget = QueueListItem("ID", "queue item name", "user", "prior", "state", "evo", "sim node", "desc")

        widget_list.addItem(qt_list_item)
        widget_list.setItemWidget(qt_list_item, list_item_widget)
        qt_list_item.setSizeHint(QSize(1, 24))
        if self.sts.ui_brightness_mode == 0:
            qt_list_item.setBackground(self.sts.state_colors[0])
        else:
            qt_list_item.setBackground(self.sts.state_colors_up[0])

        for que in self.batch.que.queue_data:
            qt_list_item = QListWidgetItem(widget_list)
            cur_color = self.sts.state_colors[que.state_id].color()
            qt_list_item.setBackground(cur_color)
            list_item_widget = QueueListItem(str(que.id), que.queue_item_name, que.user, str(que.prior), que.state,
                                             que.evolution, que.sim_node, que.description)

            widget_list.addItem(qt_list_item)
            widget_list.setItemWidget(qt_list_item, list_item_widget)
            qt_list_item.setSizeHint(QSize(130, 26))
            qt_list_item.setBackground(self.sts.state_colors[que.state_id])

    def reset_list(self):
        self.freeze_list_on_changed = 1
        index = self.batch.que.current_queue_index
        self.clear_list(with_freeze=False)
        self.init_queue_items()
        if index is not None:
            self.batch.que.current_queue_index = index
            self.batch.que.current_queue_id = self.batch.que.queue_data[self.batch.que.current_queue_index].id
            # TODO highlight q item
        self.freeze_list_on_changed = 0

    def update_all_queue(self):
        self.clear_list()
        self.init_queue_items()
        self.update_list_of_visible_ids()

    def reload_queue_data_and_refresh_list(self):
        self.batch.que.clear_all_queue_items()
        self.batch.que.load_queue()
        self.reset_list()
        self.update_list_of_visible_ids()

    def _change_current_queue_item_state_and_reset_list(self, state_id):
        self.batch.que.current_queue.state = self.sts.states_visible_names[state_id]
        self.batch.que.current_queue.state_id = state_id
        self.batch.que.save_queue()
        self.reset_list()

    def on_click_menu_set_init(self):
        self._change_current_queue_item_state_and_reset_list(self.sts.INDEX_STATE_INIT)

    def on_click_menu_set_waiting(self):
        self._change_current_queue_item_state_and_reset_list(self.sts.INDEX_STATE_WAITING)

    def on_click_menu_set_working(self):
        self._change_current_queue_item_state_and_reset_list(self.sts.INDEX_STATE_WORKING)

    def on_click_menu_set_done(self):
        self._change_current_queue_item_state_and_reset_list(self.sts.INDEX_STATE_DONE)

    def on_click_menu_set_hold(self):
        self._change_current_queue_item_state_and_reset_list(self.sts.INDEX_STATE_HOLD)

    def on_menu_locate_prev(self):
        cur_queue_item = self.batch.que.queue_data[self.batch.que.current_queue_index]
        proj_id = cur_queue_item.proj_id
        task_id = cur_queue_item.task_id
        evo_nr = cur_queue_item.evolution_nr
        version = cur_queue_item.version
        prev_dir = self.batch.dfn.get_task_prev_dir(forceProjID=proj_id, forceTaskID=task_id, evolution_nr=evo_nr,
                                                    forceQueueVersion=version)

        self.batch.logger.inf(("Task:", task_id, " prev dir: ", prev_dir))

        prev_dir = prev_dir + self.sts.dir_separator
        if self.comfun.path_exists(prev_dir, " prev open "):
            if self.sts.current_os == 1:
                pass
                # TODO linux
            else:
                subprocess.Popen('explorer "' + prev_dir + '"')

    def on_menu_open_computed_scene(self):
        cur_queue_item = self.batch.que.queue_data[self.batch.que.current_queue_index]
        # proj_id = cur_queue_item.proj_id
        task_id = cur_queue_item.task_id
        evo_nr = cur_queue_item.evolution_nr
        version = cur_queue_item.version

        file_to_load = self.batch.dfn.get_computed_setup_file(task_id, version, evo_nr)
        if file_to_load[0] == 1:
            self.batch.logger.inf(("file_to_load ", file_to_load[1]))
            self.batch.o.soft_conn.load_scene(file_to_load[1])
        else:
            self.batch.logger.wrn(("file_to_load not exist: ", file_to_load[1]))

    def on_click_menu_queue_item_remove(self):
        self.remove_queue_item()

    @staticmethod
    def on_click_menu_spacer():
        pass

    def on_right_click_show_menu(self, pos):
        global_cursor_pos = self.list_queue.mapToGlobal(pos)
        qt_right_menu = QMenu()
        # qt_right_menu.addAction("Set INIT", self.on_click_menu_set_init)
        qt_right_menu.addAction("Set WAITING", self.on_click_menu_set_waiting)
        qt_right_menu.addAction("Set WORKING", self.on_click_menu_set_working)
        qt_right_menu.addAction("Set DONE", self.on_click_menu_set_done)
        qt_right_menu.addAction("Set HOLD", self.on_click_menu_set_hold)
        qt_right_menu.addAction("________", self.on_click_menu_spacer)
        qt_right_menu.addAction("Locate prev", self.on_menu_locate_prev)
        qt_right_menu.addAction("Open computed scene", self.on_menu_open_computed_scene)
        qt_right_menu.addAction("________", self.on_click_menu_spacer)
        qt_right_menu.addAction("Remove", self.on_click_menu_queue_item_remove)
        qt_right_menu.exec_(global_cursor_pos)

    def hide_all_forms(self):
        self.qt_form_edit.hide()
        self.qt_form_remove.hide()
        self.edit_form_state = 0
        self.remove_form_state = 0

    def run_server_from_framework(self, loops=0):
        server = self.mainw.server  # .SimBatchServer(self.batch, force_local=True)
        server.force_local = True
        server.loopsLimit = loops
        server.timerDelaySeconds = 0
        server.reset_report()  # TODO
        server.run()
        report = server.generate_report()  # TODO
        if report[0] > 0:
            self.reload_queue_data_and_refresh_list()
            if report[0] == 1:
                self.top_ui.set_top_info(server.last_info, 1)
            else:
                self.top_ui.set_top_info(("total computed:", report[0], "   last", server.last_info), 6)
        else:
            if len(server.last_info) > 0:
                self.top_ui.set_top_info(server.last_info, 1)

    def on_click_sim_one(self):
        self.run_server_from_framework(loops=1)

    def on_click_sim_all(self):
        self.run_server_from_framework()

    def on_click_edit(self):
        if self.edit_form_state == 0:
            self.hide_all_forms()
            self.qt_form_edit.show()
            self.on_click_form_edit_fill()
            self.edit_form_state = 1
        else:
            self.qt_form_edit.hide()
            self.edit_form_state = 0

    def on_click_form_edit_fill(self):
        if self.batch.que.current_queue_index >= 0:
            curr_queue_item = self.batch.que.queue_data[self.batch.que.current_queue_index]
            self.qt_edit_fe_name.setText(curr_queue_item.queue_item_name)
            self.qt_edit_fe_pror.setText(str(curr_queue_item.prior))
            self.qt_edit_fe_state.setText(curr_queue_item.state)
            self.qt_fe_description.setText(curr_queue_item.description)
        else:
            self.batch.logger.wrn("Please Select Queue Item")
            self.top_ui.set_top_info(" Please Select Queue Item", 7)

    def add_queue_item_to_list(self, new_queue_item):
        wigdet_list = self.list_queue
        qt_list_item = QListWidgetItem(wigdet_list)
        qt_list_item.setBackground(QBrush(QColor("#ddd")))
        qt_list_item.setFlags(Qt.ItemFlag.NoItemFlags)
        new_queue_item = new_queue_item
        list_item_widget = QueueListItem(str(new_queue_item.id), new_queue_item.queue_item_name, new_queue_item.user,
                                         str(new_queue_item.prior), new_queue_item.state, new_queue_item.evolution,
                                         new_queue_item.sim_node, new_queue_item.description)

        wigdet_list.addItem(qt_list_item)
        wigdet_list.setItemWidget(qt_list_item, list_item_widget)
        qt_list_item.setSizeHint(QSize(1, 24))

    # def add_to_queue_and_update_list(self, form_atq):
    #     pass      TODO cleanup

    def on_click_save_changes(self, updated_queue_name, updated_prior, updated_state, updated_description):
        pass

    def on_click_remove(self):
        self.qt_form_remove.show()
    
    def remove_queue_item(self):
        if self.current_list_item_index >= 0:
            take_item_list = self.current_list_item_index + 1
            ret = self.batch.que.remove_single_queue_item(index=self.batch.que.current_queue_index, do_save=True)
            if ret:
                self.last_list_item_index = None
                self.batch.que.current_queue_index = None
                self.current_list_item_index = None
                self.list_queue.takeItem(take_item_list)
                self.qt_form_remove.hide()
                self.remove_form_state = 0
            else:
                self.batch.logger.err(("cannot remove q item from database, index: ", self.current_list_item_index))
        else:
            self.batch.logger.wrn(("cannot remove from list, element unknown for list index: ",
                                   self.current_list_item_index))

    def on_click_confirmed_remove_queue_item(self):
        self.batch.logger.db(("remove_queue_item", self.batch.que.current_queue_index,
                              self.current_list_item_index))
        self.remove_queue_item()
        self.update_list_of_visible_ids()

    def clear_list(self, with_freeze=True):
        if with_freeze:
            self.freeze_list_on_changed = 1
        while self.list_queue.count() > 0:
            self.list_queue.takeItem(0)
        if with_freeze:
            self.freeze_list_on_changed = 0

    def update_list_of_visible_ids(self):
        array_visible_queue_items_ids = []
        for que in self.batch.que.queue_data:
            if que.proj_id == self.batch.prj.current_project_id:
                array_visible_queue_items_ids.append(que.id)
        self.array_visible_queue_items_ids = array_visible_queue_items_ids

    def on_current_item_changed(self, current_queue_item):
        if self.freeze_list_on_changed == 1:   # freeze update changes on massive action    i.e  clear_list()
            self.batch.logger.deepdb(("que chngd freeze_list_on_changed", self.list_queue.currentRow()))
        else:
            self.batch.logger.inf(("list_queue_current_item_changed: ", self.list_queue.currentRow()))

            self.last_list_item_index = self.current_list_item_index
            current_list_index = self.list_queue.currentRow() - 1
            self.current_list_item_index = current_list_index

            if self.last_list_item_index is not None:
                if self.last_list_item_index is not None and self.last_list_item_index < len(self.batch.que.queue_data):
                    item = self.list_queue.item(self.last_list_item_index + 1)
                    if self.last_list_item_index < len(self.array_visible_queue_items_ids):
                        last_id = self.array_visible_queue_items_ids[self.last_list_item_index]
                        last_index = self.batch.que.get_index_by_id(last_id)
                        if item is not None and last_index is not None:
                            color_index = self.batch.que.queue_data[last_index].state_id
                            item.setBackground(self.batch.sts.state_colors[color_index].color())
                else:
                    self.batch.logger.wrn("Wrong last_que_list_index {} vs {} ".format(self.last_list_item_index,
                                                                                       len(self.batch.tsk.tasks_data)))
            else:
                self.batch.logger.db("last_task_list_index is None")

            if len(self.array_visible_queue_items_ids) <= current_list_index:
                self.update_list_of_visible_ids()  # TODO move  to init / change list
                if len(self.array_visible_queue_items_ids) > current_list_index:
                    self.batch.logger.deepdb(("vis ids FIXED: len(array_visible_queue_items_ids):",
                                              len(self.array_visible_queue_items_ids),
                                              "vs current_list_index:", current_list_index))
                else:
                    self.batch.logger.err(("vis ids NOT FIXED: len(array_visible_queue_items_ids):",
                                           len(self.array_visible_queue_items_ids),
                                           "vs current_list_index:", current_list_index))

            if 0 <= current_list_index < len(self.array_visible_queue_items_ids):
                current_queue_item_id = self.array_visible_queue_items_ids[current_list_index]
                self.batch.que.current_queue_id = current_queue_item_id
                self.batch.que.update_current_from_id(current_queue_item_id)
            else:
                self.batch.logger.err(("Wrong current_list_index: ", current_list_index,
                                       " or array_visible_queue_items_ids", len(self.array_visible_queue_items_ids)))

            current_queue_index = self.batch.que.current_queue_index
            if 0 <= current_queue_index < len(self.batch.que.queue_data):
                cur_queue = self.batch.que.queue_data[current_queue_index]
                if self.top_ui is not None:
                    self.top_ui.set_top_info("Current task: [" + str(cur_queue.id) + "]    "+cur_queue.queue_item_name)
                else:
                    self.batch.logger.err("top_ui is None")

                if current_list_index >= 0:
                    item_c = self.list_queue.item(current_list_index + 1)
                    cur_color = self.batch.sts.state_colors_up[cur_queue.state_id].color()
                    item_c.setBackground(cur_color)

                # update QUE form
                if self.edit_form_state == 1:
                    self.qt_form_edit.update_edit_ui(cur_queue)  # update edit form
            else:
                self.batch.logger.err("on chng list que {} < {}".format(current_queue_index,
                                                                        len(self.batch.que.queue_data)))
