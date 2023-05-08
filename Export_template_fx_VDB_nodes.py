"""
Export template
"""

# Built-in Imports
import os

# Local Imports
import launcher
from <studio.processor> import console
from <studio.configs> import schema
from <studio.database.context> import Context

# Third-party Imports
try:
    import pymel.core as pm
except:
    print "pymel not loaded"

TEMPLATE_PROJECT = [287, 386]  # btfm, btxp
TEMPLATE_APP = 'maya'
TEMPLATE_TASKS = ['fx', 'fx-cloud']
TEMPLATE_NAME = 'Export FX'
TEMPLATE_SHORTNAME = 'Multi Export'
TEMPLATE_TEXT = (
    "FX export template:"
    "\n- Export VDBs/AiVolume shaders in .ma file format"
)


# Helper functions -----------------------------------------------------------------------------
def has_children(obj):
    """
    Checks if the 'obj' has children or not.
    Args:
        obj: maya node's fullpath

    Returns: Bool
    """
    if pm.objExists(obj):
        children = pm.listRelatives(obj, children=True)
        print "children"
        print children
        if len(children) > 0:
            return True
        else:
            return False
    else:
        return False


# ==============================================================================================
# Main functions
# ==============================================================================================
def prep_export(self):
    """
    Use this function to show a preview of the files that will be exported and packaged.

    To add a widget to the export window:
    self.add_fileexport_widget_to_exportlist(export_name, displayed_text, filepath)

    """

    asset_id = self.task.get('entity').get('id')

    fileschema = schema.get_filename_schema('package.meshes')
    fileschema = fileschema.replace('[PROJECT]', self.project['code'])
    fileschema = fileschema.replace('[ASSET]', self.task['entity']['name'])
    fileschema = fileschema.replace('[STEP]', self.task['step']['name'])
    fileschema = fileschema.replace('[TASK]', self.task_name)
    fileschema = fileschema.replace('[BRANCH]', self.branch)
    fileschema = fileschema.replace('[VERSION]', self.current_version_string)

    filename = fileschema.split('/')[1]
    fileschema = fileschema.replace('/', os.sep)

    action_set = [{'name': 'export_FX_clouds_ma',
                   'proxy': 'fxcloud',
                   'ext': 'ma',
                   'store': 'vfx-cache',
                   'text': 'VDB group "fxcloud" will be exported as .ma to: [store->vfx-cache]'}
                  ]

    # Create widgets
    for action in action_set:
        mandatory = True
        # Pre validation, uncheck action when the group for the fx-nodes does not exist
        if action['name'] == "export_FX_clouds_ma":
            if not has_children('fxcloud|motion|'):
                mandatory = False

        # Set the full path of the future action file export, using file-schema to have the directory as well
        action_filepath = self.store_path + os.sep + action['store'] + os.sep + fileschema
        action_filepath = action_filepath.replace('[PROXY]', action['proxy']).replace('[EXT]', action['ext'])
        self.add_fileexport_widget_to_exportlist(action['name'],
                                                 action['text'],
                                                 action_filepath,
                                                 action=action,
                                                 mandatory=mandatory)


def validate(self):
    """Validates the nodes to export"""

    # Check if selected action can be performed (have mesh in them)
    msg = "An action you have selected can't be performed, does it have fx-cloud nodes to export?"
    somethingswrong = False
    for widget in self.fileexport_widgets:
        if widget.is_selected():
            if widget.action['name'] == "export_FX_clouds_ma":
                if not has_children('fxcloud|motion|'):
                    somethingswrong = True

    if somethingswrong:
        self.display_message(msg, 2)
        return False
    else:
        return True


def export(self):
    """
    Use this to export the files you need, then request toadin to package them.
    """

    # Helper functions---------------------------------------------------------
    def export_fx_ma(parent, filename):
        print("parent = ", parent)
        print("filename = ", filename)
        _children = pm.listRelatives('fxcloud|{0}'.format(parent),
                                     children=True)
        print("_children = ", _children)
        for _child in _children:
            print("_child ", _child)
            pm.parent(_child, world=True)
        pm.select(_children)

        pm.system.exportSelected(self.system_path + os.sep + filename, type='mayaAscii')
        print("Parenting _children to fxcloud...")
        for _child in _children:
            print("_child ", _child)
            pm.parent(_child, 'fxcloud|{0}'.format(parent))
        pm.select(clear=True)
    # End: Helper functions---------------------------------------------------

    # Check if pipeline server is alive
    if not console.ping():
        # Something is wrong
        print "ERROR: Pipeline server not responding..."
        return

    # Copy meta node under `root` node (in this case, `fxcloud`)
    pm.lockNode('meta', lock=False)
    pm.parent('meta', 'fxcloud')
    # Clear selection
    pm.select(clear=True)

    # Create review version
    review_version = self.db.create_reviewversion(project_id=self.project_id,
                                                  version_code=self.publish_filename,
                                                  description=self.ui.txtNote.toPlainText(),
                                                  task_id=self.task_id,
                                                  user_id=self.user_id,
                                                  file_name=self.publish_filename,
                                                  publishedfiles=self.publishedfile,
                                                  entity_type=self.task.get('entity').get('type'),
                                                  entity_id=self.task.get('entity').get('id'),
                                                  version_int=self.current_version,
                                                  branch=self.branch,
                                                  status='trev',
                                                  is_package=True)

    total = 0
    for widget in self.fileexport_widgets:
        if widget.is_selected():
            total += 1
    count = 1
    package_list = []
    for widget in self.fileexport_widgets:
        if widget.is_selected():
            filename = os.path.basename(widget.filepath)
            self.show_grey_overlay(True, "Please wait...\n" +
                                   "Performing Export & Package actions " + str(count) + " of " + str(total) + "\n" +
                                   widget.action['name'])
            if widget.action['name'] == "export_FX_clouds_ma":
                export_fx_ma('motion', filename)

            # Create the package entity
            package_code = os.path.splitext(filename)[0]
            package = self.db.create_package(project_id    =self.project_id,
                                             package_code  =filename,
                                             description   =self.ui.txtNote.toPlainText(),
                                             branch        =self.branch,
                                             proxy         =widget.action['proxy'],
                                             task_id       =self.task_id,
                                             user_id       =self.user_id,
                                             file_path     =widget.filepath,
                                             file_name     =filename,
                                             package_type  =widget.action['store'],
                                             publishedfile =self.publishedfile,
                                             entity_type   =self.task.get('entity').get('type'),
                                             entity_id     =self.task.get('entity').get('id'),
                                             version_int   =self.current_version,
                                             review_version=review_version)

            # Add the new package to the package list
            package_list.append(package)

            # Ask toadin to move it
            print "source"
            print self.system_path + os.sep + filename
            print "destination"
            print widget.filepath
            console.move_file(self.system_path + os.sep + filename,
                              widget.filepath,
                              launcher.get_user())
            count += 1

    # Clean up meta, set it back to `root` node (root is `fxcloud`)
    pm.parent('fxcloud|meta', world=True)
    pm.lockNode('meta', lock=True)
    pm.select(clear=True)
