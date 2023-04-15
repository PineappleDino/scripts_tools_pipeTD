import os
import subprocess
import logging
from functools import partial

from maya import mel, cmds
import pymel.core as pm

logging.basicConfig()
logger = logging.getLogger(name=__name__)
logger.setLevel("INFO")


class CreateBlendshapeSet(toolbar_button.ToolbarButton):
    """
    Button for creating an ObjectSet for the selected animation rig (not animation Crowd Rig), and adding to the rig's
      namespace.
    Additionally, add's the basic rig geometry into the set, needed for extracting Blendshapes from the published
      Animation Mocap Clip
    """
    name = "Create `blendshape_set` objectSet"
    icon = os.path.join(ANIM_ICONS_PATH, "blendshapes_crowd.png")
    tooltip = "Create `blendshape_set` objectSet and add to Animation Rig's namespace and its `rig_set` objectSet"

    def __init__(self, parent=None):
        super(CreateBlendshapeSet, self).__init__(self.name, self.icon, self.tooltip, parent=parent)

    @staticmethod
    def get_selected_rig_namespace():
        """
        Returns the namespace of a selected rig controller in Maya.
        :rtype: str|None
        :return: The controller's namespace, split from the controller's name string.
        """
        selection = cmds.ls(selection=True)
        if not selection:
            logger.error("Please select a rig controller!")
            return
        namespace = selection[0].split(":")[0]
        return namespace

    @staticmethod
    def get_geometry_for_blendshapes(namespace, nodes):
        """
        Returns a list of geometry nodes strings, based on namespace and nodes given
        :param str namespace: the namespace string of the rig, returned in `get_selected_rig_namespace` function. Exxample: `kidGenerator1`
        :param list nodes: the list of geometry nodes returned from the config file `blendshape_geometry`. Example: `L_lens_0001_GES`
        :rtype list[str]|None:
        :return: list of geometry nodes with the rig's respective namespace. example: 'kidGenerator1:L_lens_0001_GES'
        """
        if not namespace or not nodes:
            logger.info("No namespace or geometry nodes provided.")
            return
        geo_nodes = list()
        for node in nodes:
            if cmds.objExists("{0}:{1}".format(namespace, node)):
                geo_nodes.append("{0}:{1}".format(namespace, node))
            else:
                logger.warning("Node {0} does not exist.".format(node))

        return geo_nodes

    @staticmethod
    def create_set(namespace, rig_geos):
        """
        Generates the `blendshape_set` objectSet with geometry nodes, and parents it to the rig's `rig_set`.
        :param str namespace: str namespace: the namespace string of the rig, returned in `get_selected_rig_namespace` function. Exxample: `kidGenerator1`
        :param list[str] rig_geos: Geometry node names ['kidGenerator1:L_lens_0001_GES', ...]. Typically returned from CreateBlendshapeSet.geo_geometry_for_blendshapes()`
        """
        if not rig_geos:
            logger.error("Couldn't get geometries for 'blendshapes_set'. {0}".format(rig_geos))
            return
        # Create Set
        set_name = "{0}:{1}".format(namespace, assembly.RIG_BLENDSHAPES_SET)
        rig_set = "{0}:{1}".format(namespace, assembly.RIG_SET_NAME)

        if not pm.objExists(set_name):
            # Create 'objectSet' pymel node
            set_name = pm.createNode('objectSet', name=set_name, skipSelect=True, parent=rig_set)
            # Makes 'rig_set' string as PyNode
            rig_set = pm.PyNode(rig_set)
            # Adds 'blendshape_set' into 'rig_set'
            rig_set.addMembers(set_name)
            # Adds geometry into 'blendshape_set'
            set_name.addMembers(rig_geos)
            # Select set and merge into rig_set
            pm.select(set_name, noExpand=True)
            pm.sets(rig_set, edit=True, forceElement=set_name)
        elif pm.objExists(set_name) and not pm.sets(set_name, q=True):
            # Add just the geometry for blendshapes, if 'blendshape_set' already exists.
            logger.info("'blendshapes_set' already exists for the selected rig, but it's empty. Adding geometry.")
            new_set = pm.PyNode(set_name)
            new_set.addMembers(rig_geos)
        else:
            logger.info("'blendshapes_set' already exists for the selected rig, and contains geometry too.")

    def exec_function(self):
        # Get geometry node names from config
        blendshape_nodes = config.get("assets.publish.animation_rig.blendshape_geometry")
        # Get namespace of selected rig
        namespace = self.get_selected_rig_namespace()
        # Merge together the namespace and geometry node name into a list.
        rig_geos = self.get_geometry_for_blendshapes(namespace=namespace, nodes=blendshape_nodes)
        # Select those geometry nodes of the selected rig
        self.create_set(namespace=namespace, rig_geos=rig_geos)


