####################################
# Tested with Maya 2015 2016 2017 #
##################################
#
##
###
simbatch_installation_dir = "S:\\simbatch\\"
simbatch_config_ini = "S:\\simbatch\\config.ini"
###
##
#
import sys
sys.path.append(simbatch_installation_dir)

import core.core as simbatch_core
import ui.mainw as simbatch_ui


"""   force reload UI  START   """
reload(simbatch_core)
reload(simbatch_ui)
"""   force reload UI END   """


try:    # Maya 2015 and 2016
    import shiboken
except:
    try:  # Maya 2017
        import shiboken2 as shiboken
    except:
        print "shiboken import ERROR"


sim_batch = simbatch_core.SimBatch("Maya", ini_file=simbatch_config_ini)


"""   force reload UI  START   """
import core.settings as simbatch_settings
reload(simbatch_settings)
sim_batch.sts = simbatch_settings.Settings(sim_batch.logger, "Maya", ini_file=simbatch_config_ini)

import core.lib.common as simbatch_comfun
reload(simbatch_comfun)
sim_batch.comfun = simbatch_comfun.CommonFunctions()

import core.lib.logger as simbatch_logger
reload(simbatch_logger)
sim_batch.logger = simbatch_logger.Logger()

import core.projects as simbatch_projects
reload(simbatch_projects)
sim_batch.prj = simbatch_projects.Projects(sim_batch)

import core.schemas as simbatch_schemas
reload(simbatch_schemas)
sim_batch.sch = simbatch_schemas.Schemas(sim_batch)

import core.tasks as simbatch_tasks
reload(simbatch_tasks)
sim_batch.tsk = simbatch_tasks.Tasks(sim_batch)

import core.queue as simbatch_queue
reload(simbatch_queue)
sim_batch.que = simbatch_queue.Queue(sim_batch)

import core.nodes as simbatch_nodes
reload(simbatch_nodes)
sim_batch.nod = simbatch_nodes.SimNodes(sim_batch)

import core.definitions as simbatch_definitions
reload(simbatch_definitions)
sim_batch.dfn = simbatch_definitions.Definitions(sim_batch)

import core.io as simbatch_ios
reload(simbatch_ios)
sim_batch.sio = simbatch_ios.StorageInOut(sim_batch)
"""   force reload UI END   """

loading_data_state = sim_batch.load_data()


if sim_batch.sts.WITH_GUI == 1:
    """   force reload UI  START   """
    import ui.ui_settings as simbatch_ui_settings
    reload(simbatch_ui_settings)
    import ui.ui_projects as simbatch_ui_projects
    reload(simbatch_ui_projects)
    import ui.ui_schemas as simbatch_ui_schemas
    reload(simbatch_ui_schemas)
    import ui.ui_schemas_form as simbatch_ui_schemas_form
    reload(simbatch_ui_schemas_form)
    import ui.ui_tasks as simbatch_ui_tasks
    reload(simbatch_ui_tasks)
    import ui.ui_tasks_form as simbatch_ui_tasks_form
    reload(simbatch_ui_tasks_form)
    import ui.ui_tasks as simbatch_ui_tasks
    reload(simbatch_ui_tasks)
    import ui.ui_queue as simbatch_ui_queue
    reload(simbatch_ui_queue)
    import ui.ui_definitions as simbatch_ui_definitions
    reload(simbatch_ui_definitions)
    import server.server as simbatch_server
    reload(simbatch_server)
    import ui.ui_nodes as simbatch_nodes
    reload(simbatch_nodes)
    reload(simbatch_ui)
    """   force reload UI END   """
    main_window = simbatch_ui.MainWindow(sim_batch)
    main_window.show()
    main_window.post_run(loading_data_state)
