#
# For network and multi node implementation
# please ask about PRO version
#
#  www.SimBatch.com
#
# JSON Name Format, PEP8 Name Format
NODES_ITEM_FIELDS_NAMES = [
    ('id', 'id'),
    ('name', 'node_name'),
    ('stateId', 'state_id'),
    ('state', 'state'),
    ('stateFile', 'state_file'),
    ('desc', 'description')]


class SingleNode:
    totalItems = 0
    max_id = 0
    def __init__(self, id, nodeName, state, state_id, state_file, description):
        if id > 0:
            SingleNode.max_id = id
        else:
            SingleNode.max_id += 1
        SingleNode.totalItems += 1

        self.id = SingleNode.max_id
        self.node_name = nodeName
        self.state = state
        self.state_id = state_id
        self.state_file = state_file
        self.description = description


class SimNodes:
    batch = None
    comfun = None

    nodes_data = []
    total_nodes = 0

    current_node_id = None
    current_node_index = None
    current_node = None

    max_id = 0

    def __init__(self, batch):
        self.batch = batch
        self.comfun = batch.comfun
        self.nodes_data = []

    def print_current(self):
        if self.current_node_index is not None and self.current_node_index > 0:
            n = self.nodes_data[self.current_node_index]
            self.batch.logger.raw((" node: ", n.nodeName, n.state, n.description))
        else:
            self.batch.logger.raw((" no current node, index: ", self.current_node_index))

    def print_all(self):
        for n in self.nodes_data:
            self.batch.logger.raw((" node: ", n.nodeName, n.state, n.description))

    #  update id, index and current for fast use by all modules
    def update_current_from_index(self, index):
        if 0 <= index < self.total_nodes:
            self.current_node_index = index
            self.current_node_id = self.nodes_data[index].id
            self.current_node = self.nodes_data[index]
            return True
        else:
            self.current_node_id = None
            self.current_node = None
            self.batch.logger.err(("(update_current_from_index) wrong index:", index))
            self.batch.logger.err(" total:{}  len:{}".format(self.total_nodes, len(self.nodes_data)))
            return False

    def add_simnode(self, single_node):
        if single_node.id > 0:
            self.max_id = single_node.id
        else:
            self.max_id += 1
            single_node.id = self.max_id
        self.nodes_data.append(single_node)
        self.total_nodes += 1

    def load_nodes(self):
        if self.batch.sts.store_data_mode == 1 :
            self.load_nodes_from_json()
        if self.batch.sts.store_data_mode == 2 :
            self.load_nodes_from_mysql()

    def load_nodes_from_json(self, json_file=""):
        if len(json_file) == 0:
            json_file = self.batch.sts.store_data_json_directory + self.batch.sts.JSON_SIMNODES_FILE_NAME
        if self.comfun.file_exists(json_file, info="simnodes file"):
            self.batch.logger.inf(("loading simnode items: ", json_file))
            json_nodes = self.comfun.load_json_file(json_file)
            if json_nodes is not None and "simnodes" in json_nodes.keys():
                if json_nodes['simnodes']['meta']['total'] > 0:
                    for li in json_nodes['simnodes']['data'].values():
                        if len(li) == len(NODES_ITEM_FIELDS_NAMES):
                            new_simnode_item = SingleNode(int(li['id']), li['name'], li['state'],
                                                          int(li['stateId']), li['stateFile'], li['desc'])
                            self.add_simnode(new_simnode_item)
                        else:
                            self.batch.logger.wrn(("simnode json data not consistent:", len(li),
                                                   len(NODES_ITEM_FIELDS_NAMES)))
                    return True
            else:
                self.batch.logger.wrn(("no tasks data in : ", json_file))
                return False
        else:
            self.batch.logger.wrn(("no schema file: ", json_file))
            return False

    def load_nodes_from_mysql(self):
        # PRO VERSION
        self.batch.logger.inf("MySQL will be supported with the PRO version")
        return None

    def save_nodes(self):
        if self.batch.sts.store_data_mode == 1:
            self.save_nodes_to_json()
        if self.batch.sts.store_data_mode == 2:
            self.save_nodes_to_myqsl()

    def save_nodes_to_json(self, json_file=None):
        if json_file is None:
            json_file = self.sts.store_data_json_directory + self.sts.JSON_SIMNODES_FILE_NAME
        content = self.format_nodes_data(json=True)
        return self.comfun.save_json_file(json_file, content)

    def format_nodes_data(self, json=False, sql=False, backup=False):
        if json == sql == backup == False:
            self.batch.logger.err("(format_nodes_data) no format param !")
        else:
            if json or backup:
                tim = self.comfun.get_current_time()
                formated_data = {"simnodes": {"meta": {"total": self.total_nodes,
                                                       "timestamp": tim,
                                                       "jsonFormat": "http://json-schema.org/"
                                                       },
                                              "data": {}}}
                for i, td in enumerate(self.nodes_data):
                    nod = {}
                    for field in NODES_ITEM_FIELDS_NAMES:
                        nod[field[0]] = eval('td.'+field[1])
                    formated_data["simnodes"]["data"][i] = nod
                return formated_data
            else:
                # PRO version with SQL
                return False

    def save_nodes_to_myqsl(self):
        ### PRO VERSION
        self.batch.logger.inf("PRO version with SQL")

    def clear_all_nodes(self):
        del self.nodes_data[:]
        self.max_id = 0
        self.total_nodes = 0
        self.lastNodeNr = -1
        self.currentNodeNr = -1

    def get_node_state(self, file):  ### TODO tryToCreateIfNotExist = False,
        if self.comfun.file_exists(file, "get state file txt"):
            f = open(file, 'r')
            firstLine = f.readline()
            f.close()
            if len(firstLine) > 0:
                li = firstLine.split(";")
            else:
                li = [-1]
                self.batch.logger.deepdb((" [db] len(firstLine) : ", len(firstLine), " ___ ", len(firstLine)))

            stateInt = self.comfun.int_or_val(li[0], -1);
            self.batch.logger.deepdb((" [db] get stateInt : ", stateInt))
            return stateInt
        else:
            return -1

    def set_node_state(self, file, serverName, state):
        if self.comfun.fileExists(file, "set state file txs"):
            self.batch.logger.deepdb((" [db] set state : ", state))
            f = open(file, 'w')
            f.write(str(state) + ";" + serverName + ";" + self.comfun.getCurrentTime())
            f.close()
        else:
            self.batch.logger.err(("[ERR] file set state not exist: ", file))



#
# For network and multi node implementation
# please ask about PRO version
#
#  www.SimBatch.com
#
