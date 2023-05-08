import logging
import os

from <studio.config> import config
from <studio.pipeline> import User, Task
from <studio.pipeline.asset> import Asset, AssetType
from <studio.pipeline.classes.asset_components> import <studio-filetype-for_meshes-interface>
from <studio.pipeline.classes.asset_versions> import <studio-FXCache-Asset-Version>
from <studio.utilities.workspace> import get_workspace_path
from <studio-maya-api.asset> import io
from maya import cmds
from pymel import core as pm

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def create_meshcache_asset_version(
        label, component_label=<studio-filetype-for_meshes-interface>.<DEFAULT_STUDIOFILETYPE_COMPONENT>,
        save_scene=True, user=None, task=None):
    ''' Creates a new FX Cache user version with the given label
    
    :param str label: The asset label
    :param str component_label: The component label (do not create component if None)
    :param bool save_scene: If true, automatically save a copy of the current scene as the master scene
    :param User user: Create a version for this user
    :param Task task: Create a version in this task
    
    :rtype: FXCacheAssetVersion
    '''
    if not task:
        task = Task()
    if not user:
        user = User()
    asset = Asset.make_from_task_label_type(task, label, AssetType('FX Cache'))
    asset_version = <studio-FXCache-Asset-Version>.make_version(asset, user, asset.get_next_user_version(), task)
    asset_version.add_master_scene_component('ma')
    if save_scene:
        io.save_current_scene(asset_version.master_scene_component)
    if component_label:
        asset_version.add_meshcache_component(label=component_label)
    asset_version.save()
    return asset_version


def do_create_geometry_cache(time_range_mode=2, start_frame=1, end_frame=10, cache_file_distribution="OneFile",
                             refresh=1, cache_directory="", cache_per_geo=0, cache_name="", name_as_prefix=0,
                             cache_action="add", force_save=0, sim_rate=1, sample_multiplier=1, inherit_modifications=0,
                             floats=1, cache_format="mcx", export_in_world_space=0):
    """
    Wrapper for command MEL script 'doCreateGeometryCache'. (Uses $version param as 6 for all new args)
    Script located in autodesk Maya's installation directory:
        <location-softwares>/autodesk/maya/linux_64/[maya-version]/scripts/others/doCreateGeometryCache.mel
    example MEL command:
        doCreateGeometryCache 6 { "2", "1", "10", "OneFile", "1", "","0","","0", "add", "0", "1", "1","0","1","mcx","0" } ;
    Function in MEL script: global proc string[] doCreateGeometryCache( int $version, string $args[] )
    -------------------------------
    Create cache files on disk for the selected shape(s) according to the specified flags described below.

    :param int time_range_mode:
        time range mode = 0 : use 'start_frame' and 'end_frame' as start-end
        time range mode = 1 : use render globals
        time range mode = 2 : use timeline
    :param int start_frame: start frame (if time range mode == 0)
    :param int end_frame: end frame (if time range mode == 0)
    :param str cache_file_distribution: cache file distribution, either "OneFile" or "OneFilePerFrame"
    :param int refresh: 0/1, whether to refresh during caching
    :param str cache_directory: directory for cache files, if "", then use project data dir
    :param int cache_per_geo: 0/1, whether to create a cache per geometry
    :param str cache_name: name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.
    :param int name_as_prefix: 0/1, whether the specified cache name is to be used as a prefix
    :param str cache_action: action to perform: "add", "replace", "merge", "mergeDelete" or "export"
    :param int force_save: 0/1, force save even if it overwrites existing files
    :param int sim_rate: simulation rate, the rate at which the cloth simulation is forced to run
    :param int sample_multiplier: sample mulitplier, the rate at which samples are written, as a multiple of simulation rate.
    :param int inherit_modifications: 0/1, whether modifications should be inherited
        from the cache about to be replaced. Valid only when $action == "replace".
    :param int floats: 0/1, whether to store doubles as floats
    :param str cache_format: name of cache format ("mcx"/"mcc")
    :param int export_in_world_space: 0/1, whether to export in local or world space
    """
    pm.mel.doCreateGeometryCache(6, [
        str(time_range_mode),
        str(start_frame),
        str(end_frame),
        cache_file_distribution,
        str(refresh),
        cache_directory,
        str(cache_per_geo),
        cache_name,
        str(name_as_prefix),
        cache_action,
        str(force_save),
        str(sim_rate),
        str(sample_multiplier),
        str(inherit_modifications),
        str(floats),
        cache_format,
        str(export_in_world_space)
    ])


def delete_cache_file(cache_name="face_rig_geometry_cache"):
    """
    Deletes the geometry cache node, along with its respective files in /data/caches/nCache

    :param str cache_name: name of the geometry cache node. (shared with the cache file name too)
    """
    cache_node = "{0}Cache1".format(cache_name)
    if cmds.objExists(cache_node):
        # gets path attribute of the geometry cache, where files are located.
        base_dir = cmds.getAttr("{0}Cache1.cachePath".format(cache_name))
        files_in_dir = os.listdir(base_dir)
        cmds.delete(cache_node)
        for file in files_in_dir:
            ext = file.split(".")[-1]
            if ext in ("xml", "mcx", "mcc") and cache_name in file:
                os.remove(base_dir + file)


def check_for_cache_files(cache_name="face_rig_geometry_cache", slots=None):
    """
    Checks if there are cache files in /data/caches/nCache, and if the cache geometry node exists.

    :param str cache_name: name of the geometry cache node (shared with the cache file name too)
    :param list[str] slots: the shotbundle container slots name strings.
    :rtype: bool
    :return: If there is a cache node and cache files, returns True.
    """
    if slots is None:
        slots = []

    cache_directory = "{0}/data/caches/nCache/".format(get_workspace_path(app='maya', task=Task(), user=User()))
    if not os.path.isdir(cache_directory):
        return False
    maya_scene_data_path = os.listdir(cache_directory)
    if not maya_scene_data_path:
        return False

    for slot in slots:
        # Checks if there is cache geometry generated for the slot
        cache_name = "{slot}_{cache_name}".format(slot=slot, cache_name=cache_name)
        if cmds.objExists("{0}Cache1".format(cache_name)):
            # Lists files in /data/caches/nCache/[maya_scene name]
            files_in_maya_scene_data_path = os.listdir("{0}{1}".format(cache_directory, maya_scene_data_path[0]))
            for file_in_maya_scene_data_path in files_in_maya_scene_data_path:
                # Checks if the file's name is same as cache_name.
                if cache_name in file_in_maya_scene_data_path:
                    return True
    return False

def return_geometry_cache_nodes(cache_name="face_rig_geometry_cache", slots=None):
    """
    Returns geometry cache nodes (non-DAG) present in the scene. Similar to `check_for_cache_files`.

    :param str cache_name: name of the geometry cache node (shared with the cache file name too)
    :param list[str] slots: the shotbundle container slots name strings.
    :rtype: list[str]
    :return: geometry cache nodes under the `cache_name` provided.
    """
    if slots is None:
        slots = []

    geometry_cache_nodes = []
    for slot in slots:
        slot_cache_name = "{slot}_{cache_name}".format(slot=slot, cache_name=cache_name)
        if cmds.objExists("{0}Cache1".format(slot_cache_name)):
            geometry_cache_nodes += cmds.ls("{0}Cache1".format(slot_cache_name))
    return geometry_cache_nodes


def cache_facial_animation_geometry(create=False, delete=False, slot=None):
    """
    Generates geometry cache of head geometry proxy nodes.
    Note: Specify only 'create' or 'delete' as True, per call of this function. They are mutually exclusive.

    :param bool create: Creates the facial geometry cache. This option takes precedence.
    :param bool delete: Deletes the facial geometry cache.
    :param str slot: name of the slot to generate or delete geometry cache from.
    """
    if create == delete:
        logger.error("Parameters defined incorrectly. Please define only one option as True.")
        return

    if not slot:
        logger.error("A shotbundle slot name was not provided.")
        return

    # Config listing the common geometry proxy face names used by most rigs.
    geo_proxy_face_names = config.get("maya.modelling_naming.geo_proxy_face_names")
    list_face_geometry = []

    # Checks if each "face_geo" node exists the maya scene for the slot.
    for face_geo in geo_proxy_face_names:
        if cmds.objExists("{0}:{1}".format(slot, face_geo)):
            # Checks if Shape node exists:
            if cmds.objExists("{0}:{1}Shape".format(slot, face_geo)):
                list_face_geometry.append("{0}:{1}".format(slot, face_geo))
    if not list_face_geometry:
        logger.error("This rig does not contain any proxy-nodes! Cannot create facial geometry cache.")
        return
    logger.info("Proxy Geometries in {0}: {1}".format(slot, list_face_geometry))

    cmds.select(clear=True)
    # Selects the facial proxy geometry nodes of the slot.
    for geo_node in list_face_geometry:
        cmds.select(geo_node, add=True)

    if create:
        do_create_geometry_cache(time_range_mode=2,
                                 start_frame=1,
                                 end_frame=10,
                                 cache_file_distribution="OneFile",
                                 refresh=1,
                                 cache_directory="",
                                 cache_per_geo=0,
                                 cache_name="{0}_face_rig_geometry_cache".format(slot),
                                 name_as_prefix=0,
                                 cache_action="add",
                                 force_save=1,
                                 sim_rate=1,
                                 sample_multiplier=1,
                                 inherit_modifications=0,
                                 floats=1,
                                 cache_format="mcx",
                                 export_in_world_space=0)
        cmds.select(clear=True)

    elif delete:
        delete_cache_file(cache_name="{0}_face_rig_geometry_cache".format(slot))
        cmds.select(clear=True)


