import os
import copy

# JSON Name Format, PEP8 Name Format
QUEUE_ITEM_FIELDS_NAMES = [
    ('id', 'id'),
    ('name', 'queue_item_name'),
    ('taskId', 'task_id'),
    ('user', 'user'),
    ('userId', 'user_id'),
    ('sequence', 'sequence'),
    ('shot', 'shot'),
    ('take', 'take'),
    ('frameFrom', 'frame_from'),
    ('frameTo', 'frame_to'),
    ('state', 'state'),
    ('stateId', 'state_id'),
    ('ver', 'version'),
    ('evo', 'evolution'),
    ('evoNr', 'evolution_nr'),
    ('evoScript', 'evolution_script'),
    ('prior', 'prior'),
    ('desc', 'description'),
    ('simNode', 'sim_node'),
    ('simNodeId', 'sim_node_id'),
    ('time', 'time'),
    ('projId', 'proj_id'),
    ('softId', 'soft_id')
    ]


class QueueItem:
    def __init__(self, queue_item_id, queue_item_name, task_id, user, user_id, sequence, shot, take,
                 frame_from, frame_to, state, state_id, ver, evo, evo_nr, evo_script, prior,
                 description, sim_node, sim_node_id, time, proj_id, soft_id):
        self.id = queue_item_id
        self.queue_item_name = queue_item_name
        self.task_id = task_id
        self.user = user
        self.user_id = user_id
        self.sequence = sequence
        self.shot = shot
        self.take = take
        self.frame_from = frame_from
        self.frame_to = frame_to
        self.state = state
        self.state_id = state_id
        self.version = ver
        self.evolution = evo
        self.evolution_nr = evo_nr
        self.evolution_script = evo_script
        self.prior = prior
        self.description = description
        self.sim_node = sim_node
        self.sim_node_id = sim_node_id
        self.time = time
        self.proj_id = proj_id   # TODO  change to project_id
        self.soft_id = soft_id


class Queue:
    batch = None
    comfun = None

    queue_data = []
    total_queue_items = 0
    max_id = 0

    current_queue_id = None
    current_queue_index = None
    current_queue = None

    sample_data_checksum = 0
    sample_data_total = 0

    def __init__(self, batch):
        self.batch = batch
        self.sts = batch.sts
        self.comfun = batch.comfun
        self.queue_data = []

    #  print project data, mainly for debug
    def print_header(self):
        print "\n QUEUE: "
        print "     current queue item id: {}   index: {}   total queue items: {}\n".format(self.current_queue_id,
                                                                                            self.current_queue_index,
                                                                                            self.total_queue_items)

    def print_current(self):
        print "       current queue index:{}, id:{}, total:{}".format(self.current_queue_index, self.current_queue_id,
                                                                      self.total_queue_items)
        if self.current_queue_index is not None:
            cur_que = self.current_queue
            print "       current queue name:{}".format(cur_que.queue_item_name)

    def print_all(self):
        if self.total_queue_items == 0:
            print "   [INF] no queu items loaded"
        for q in self.queue_data:
            print "\n\n {}  {}  {}  {} state:{}   evo:{}   simnode:{}  desc:{}".format(q.id, q.queue_item_name, q.prior,
                                                                                       q.proj_id, q.state, q.evolution,
                                                                                       q.sim_node, q.description,
                                                                                       q.proj_id)
        print "\n\n"

    @staticmethod
    def get_blank_queue_item():
        return QueueItem(0, "", 1, "M", 1, "", "", "", 10, 20, "NULL", 0, 1, "", 0, "", 50, " 1 ", "", 0, "", 1, 3)

    def get_index_by_id(self, get_id):
        for i, que in enumerate(self.queue_data):
            if que.id == get_id:
                return i
        self.batch.logger.wrn(("(get index by id) no queue item with id: ", get_id))
        return None

    def update_current_from_id(self, queue_id):
        for i, que in enumerate(self.queue_data):
            if que.id == queue_id:
                self.current_queue_index = i
                self.current_queue_id = queue_id
                self.current_queue = que
                return i
        self.clear_current_queue_item()
        return False

    def clear_current_queue_item(self):
        self.current_queue_id = None
        self.current_queue_index = None
        self.current_queue = None

    def get_first_with_state_id(self, state_id, soft=0):
        for index, q in enumerate(self.queue_data):
            if q.state_id == state_id:
                if soft > 0:
                    if q.soft_id == soft:
                        return index, self.queue_data[index].id
                else:
                    return index, self.queue_data[index].id
        return -1, -1

    def update_state_and_node(self, queue_id, state, state_id, server_name="", server_id=-1, set_time=0,
                              add_current_time=False):
        for i, q in enumerate(self.queue_data):
            if q.id == queue_id:
                self.queue_data[i].state = state
                self.queue_data[i].state_id = state_id
                self.queue_data[i].sim_node = server_name
                self.queue_data[i].sim_node_id = server_id
                if add_current_time:
                    self.queue_data[i].description = "[{}]  {}".format(self.comfun.get_current_time(only_time=True),
                                                                       self.queue_data[i].description)
                elif set_time > 0:
                    time_string = self.comfun.format_seconds_to_string(set_time)
                    self.queue_data[i].description = "[{}]  {}".format(time_string, self.queue_data[i].description)
                return True
        return False

    def delete_json_queue_file(self, json_file=None):
        if json_file is None:
            json_file = self.sts.store_data_json_directory_abs + self.sts.JSON_QUEUE_FILE_NAME
        if self.comfun.file_exists(json_file):
            return os.remove(json_file)
        else:
            return True

    @staticmethod
    def clear_queue_items_in_mysql():
        # PRO VERSION with sql
        return False

    def clear_all_queue_items(self, clear_stored_data=False):
        del self.queue_data[:]
        self.max_id = 0
        self.total_queue_items = 0
        self.current_queue_id = None
        self.current_queue_index = None
        # TODO check clear UI val (last current...)
        if clear_stored_data:
            if self.sts.store_data_mode == 1:
                if self.delete_json_queue_file():
                    return True
                else:
                    return False
            if self.sts.store_data_mode == 2:
                if self.clear_queue_items_in_mysql():
                    return True
                else:
                    return False
        return True

    def add_to_queue(self, queue_items, do_save=False):
        last_queue_item_id = None
        for queue_item in queue_items:
            if queue_item.id > 0:
                self.max_id = queue_item.id
            else:
                self.max_id += 1
                queue_item.id = self.max_id
            last_queue_item_id = self.max_id
            self.queue_data.append(queue_item)
            self.total_queue_items += 1

        if do_save is True:
            if self.save_queue():
                return last_queue_item_id
            else:
                return False
        return last_queue_item_id

    def remove_single_queue_item(self, index=None, queue_id=None, do_save=False):
        if index is None and queue_id is None:
            self.batch.logger.err("queue item data not removed, skipping, missing index or id!")
            return False
        removed = False
        if queue_id > 0:
            for i, que in enumerate(self.queue_data):
                if que.id == queue_id:
                    del self.queue_data[i]
                    self.total_queue_items -= 1
                    removed = True
                    break
        if index >= 0:
            del self.queue_data[index]
            self.total_queue_items -= 1
            removed = True
        if removed:
            if do_save is True:
                return self.save_queue()
            else:
                return True
        else:
            self.batch.logger.err("queue item data not removed, item not found!")
            return False

    def generate_template_queue_item(self, task_id, options=None):
        # TODO
        # TODO   WIP
        task_index = self.batch.tsk.get_index_by_id(task_id)
        if task_index is not None:
            task_to_queued = self.batch.tsk.tasks_data[task_index]
            schema_index = self.batch.sch.get_index_by_id(task_to_queued.schema_id)
            schema_to_queued = self.batch.sch.schemas_data[schema_index]

            task_to_queued.queue_ver += 1
            current_time = ""

            new_queue_item = QueueItem(0, "queue item 2", task_to_queued.id, "U", 0,
                                       task_to_queued.sequence, task_to_queued.shot, task_to_queued.take,
                                       task_to_queued.sim_frame_start, task_to_queued.sim_frame_end,
                                       self.batch.sts.states_visible_names[self.batch.sts.INDEX_STATE_WAITING],
                                       self.batch.sts.INDEX_STATE_WAITING,
                                       task_to_queued.queue_ver, "evo", 0, "evo_script",
                                       task_to_queued.priority, "", "", -1, current_time, task_to_queued.project_id,
                                       schema_to_queued.soft_name)

            # TODO
            # TODO
            print "\n  !!! TODO compile2 ...  WIP ... ", task_id, options
            return new_queue_item    # self.get_blank_queue_item()
        else:
            return None

    def generate_queue_items(self, task_id, options=None):
        # TODO   WIP
        queue_items = []
        template_queue_item = self.generate_template_queue_item(task_id, options=None)
        evolutions = ["BND:4", "BND:5", "BND:7"]    # HACK TODO
        for i, evo in enumerate(evolutions):
            queue_item = copy.deepcopy(template_queue_item)
            queue_item.evo = evo
            queue_item.evo_nr = i
            queue_item.evo_script = self.generate_evo_script(evo)
            queue_item.description = evo
            queue_items.append(queue_item)
        return queue_items

    # prepare 'queue_data' for backup or save
    def format_queue_data(self, json=False, sql=False, backup=False):
        if json == sql == backup is False:
            self.batch.logger.err("(format_queue_data) no format param !")
        else:
            if json or backup:
                tim = self.comfun.get_current_time()
                formated_data = {"queueItems": {"meta": {"total": self.total_queue_items,
                                                         "timestamp": tim,
                                                         "jsonFormat": "http://json-schema.org/"},
                                                "data": {}}}
                for i, qu in enumerate(self.queue_data):
                    que = {}
                    for field in QUEUE_ITEM_FIELDS_NAMES:
                        que[field[0]] = eval('qu.'+field[1])
                    formated_data["queueItems"]["data"][i] = que
                return formated_data
            else:
                # PRO version with SQL
                return False

    def create_example_queue_data(self, do_save=True):
        collect_ids = 0
        sample_queue_item_1 = QueueItem(0, "queue item 1", 1, "T", 1, "", "", "", 1, 2, "DONE", 11, 3, "", 0,
                                        "script", 50, "first", "sim_01", 1, "2017_12_28 02:02:02", 1, 1)
        sample_queue_item_2 = QueueItem(0, "queue item 2", 3, "T", 1, "", "", "", 3, 4, "WORKING", 4, 2, "", 0,
                                        "script", 50, "second", "sim_01", 1, "2018_06_20 02:02:03", 1, 1)
        sample_queue_item_3 = QueueItem(0, "queue item 3", 4, "T", 1, "", "", "", 5, 6, "WAITING", 2, 1, "", 0,
                                        "script", 40, "third", "sim_01", 1, "2018_06_20 02:02:04", 1, 1)
        collect_ids += self.add_to_queue((sample_queue_item_1, ))
        collect_ids += self.add_to_queue((sample_queue_item_2, ))
        collect_ids += self.add_to_queue((sample_queue_item_3, ), do_save=do_save)

        self.sample_data_checksum = 6
        self.sample_data_total = 3
        return collect_ids

    def load_queue(self):
        if self.sts.store_data_mode == 1:
            return self.load_queue_from_json()
        if self.sts.store_data_mode == 2:
            return self.load_queue_from_mysql()

    def load_queue_from_json(self, json_file=""):
        if len(json_file) == 0:
            json_file = self.sts.store_data_json_directory_abs + self.sts.JSON_QUEUE_FILE_NAME
        if self.comfun.file_exists(json_file, info="queue file"):
            self.batch.logger.db(("loading queue items: ", json_file))
            json_nodes = self.comfun.load_json_file(json_file)
            if json_nodes is not None and "queueItems" in json_nodes.keys():
                if json_nodes['queueItems']['meta']['total'] > 0:
                    for li in json_nodes['queueItems']['data'].values():
                        if len(li) == len(QUEUE_ITEM_FIELDS_NAMES):
                            new_queue_item = QueueItem(int(li['id']), li['name'], int(li['taskId']), li['user'],
                                                       int(li['userId']), li['sequence'], li['shot'], li['take'],
                                                       int(li['frameFrom']), int(li['frameTo']),
                                                       li['state'], int(li['stateId']), li['ver'],
                                                       li['evo'], int(li['evoNr']), li['evoScript'], int(li['prior']),
                                                       li['desc'], li['simNode'], int(li['simNodeId']),
                                                       li['time'], int(li['projId']), "TMP")  # TODO int(li['softId'])
                            self.add_to_queue((new_queue_item, ))
                        else:
                            self.batch.logger.wrn(("queue json data not consistent:",
                                                   len(li), len(QUEUE_ITEM_FIELDS_NAMES)))
                    return True
            else:
                self.batch.logger.wrn(("no tasks data in : ", json_file))
                return False
        else:
            self.batch.logger.wrn(("queue file doesn't exist: ", json_file))
        return False

    def load_queue_from_mysql(self):
        # PRO VERSION
        self.batch.logger.inf("MySQL will be supported with the PRO version")
        return None

    def save_queue(self):
        if self.sts.store_data_mode == 1:
            return self.save_queue_to_json()
        if self.sts.store_data_mode == 2:
            return self.save_queue_to_mysql()

    def save_queue_to_json(self, json_file=None):
        if json_file is None:
            json_file = self.sts.store_data_json_directory_abs + self.sts.JSON_QUEUE_FILE_NAME
        content = self.format_queue_data(json=True)
        return self.comfun.save_json_file(json_file, content)

    def save_queue_to_mysql(self):
        # PRO VERSION
        self.batch.logger.inf("MySQL will be supported with the PRO version")
        return None
