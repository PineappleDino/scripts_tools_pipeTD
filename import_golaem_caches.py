"""
Script for copying cache golaem files to maya workspace.
"""
import os
import sys
import json
import shutil

# Local Imports
import launcher
from <local_studio_api> import dbio, fsio

# Maya imports
from maya import cmds

# Global Constants
SCRIPT_NAME = "<SHOTGRID_SCRIPT_ACCOUNT_NAME>"
API_KEY = "<_APIKEY_FROM_SHOTGUN_>"
current_config = launcher.get_current_config()
project_id = int(current_config['project_id'])

# Instances DBIO
db = dbio.DB(launcher.get_shotgun_site_url(), SCRIPT_NAME, API_KEY)


def progress(count, total, status=''):
    """
    A progress bar to display the progress of getting shot tasks.

    :param: int count: the iteration variable
    :param: int total: total of variable ammounts
    :param: str status: 
    (from: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3)
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def get_workspace_path():
    """
    Gets the current workspace's path (with the current shot/task environment)
    """

    # Get Metadata
    task_id = cmds.getAttr('meta.task_id')
    project_id = int(current_config['project_id'])

    # Get workspace
    path = fsio.FS().get_task_workspace_path(
        db.get_project(project_id),
        db.get_task(project_id=project_id, task_id=task_id),
        db)

    return path


def get_crowd_cache_package(shot_id=None, shot_name=None):
    """
    Gets the latest "crowd-cache" package available in the shot and returns its files and directory.
    """
    if shot_id:
        crowd_cache_package = db.get_latest_shot_package(project_id, shot_id=int(shot_id), type="crowd-cache")
    if shot_name:
        crowd_cache_package = db.get_latest_shot_package(project_id, type="crowd-cache", asset_name=shot_name)
    if not crowd_cache_package:
        cmds.error("No crowd-cache file package found!")
        return
    return crowd_cache_package


def update_gscb_paths(crowd_cache_files, workspace_path):
    """
    Find the .gscb files in the crowd-cache package, updates its paths to match the current shot's Maya workspace.

    """
    gscb_file = ''
    gscl_file = ''
    gtg_file = ''
    workspace_path = fsio.path_converter(workspace_path, 'linux')
    for _file in crowd_cache_files:
        _file = fsio.path_converter(_file, 'linux')
        if ".gscb" in _file: # ['libFile']
            gscb_file = '/{0}/maya/cache{1}'.format(workspace_path, _file)
        elif ".gscl" in _file: # ['items']['layoutFile']
            gscl_file = '/{0}/maya/cache{1}'.format(workspace_path, _file)
        elif ".gtg" in _file: # ['items']['sourceTerrain']
            gtg_file = '/{0}/maya/cache{1}'.format(workspace_path, _file)

    if os.path.exists(gscb_file):
        # Key 'items': [cacheDir, layoutFile, sourceTerrain], key 'LibFile'
        with open(gscb_file, "r") as json_file:
            data = json.load(json_file)
        
        for items in data['items']:
            if os.path.exists(gscb_file):
                items['cacheDir'] = '/{0}/maya/cache'.format(workspace_path)
            if os.path.exists(gscl_file):
                items['layoutFile'] = gscl_file
            if os.path.exists(gtg_file):
                items['sourceTerrain'] = gtg_file
        data['libFile'] = gscb_file

        with open(gscb_file, "w+") as json_file:
            json.dump(data, json_file, indent=4)

    else:
        cmds.error("Can't find .gscb file to update paths.")


def copy_crowd_cache_to_maya_workspace(import_from_another_shot=False):
    """
    Copies the files from the "crowd-cache" package, into the shot's maya workspace.
    Will copy files into shot's '/workspace/maya/cache' directory.
    And update the copied '.gscb' file to match new location.
    """

    # Get Shot Metadata
    shot_id = cmds.getAttr('meta.shot_id')
    package = None
    if not import_from_another_shot:
        package = get_crowd_cache_package(shot_id=shot_id)
    else:
        result = cmds.promptDialog(
            title='Copy crowd-cache from another shot',
            message='Enter Shot name to copy cache from:',
            messageAlign='center',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel',
            style='text'
        )
        if result == 'OK':
            shot_name = cmds.promptDialog(query=True, text=True)
            package = get_crowd_cache_package(shot_name=shot_name)

    workspace_path = get_workspace_path()
    
    path_package = package['sg_sfs_path']
    files_package = os.listdir(path_package)

    # copy files to shot's maya workspace 'cache' folder
    progress_count = 0
    for _file in files_package:
        shutil.copy2(
            src="{0}\{1}".format(path_package, _file),
            dst="{0}\maya\cache".format(workspace_path)
        )
        progress_count += 1 # counter for progress bar.
        progress(count=progress_count, total=len(files_package), status="Copying {0}".format(_file))
    
    if import_from_another_shot:
        update_gscb_paths(crowd_cache_files=files_package, workspace_path=workspace_path)
    

