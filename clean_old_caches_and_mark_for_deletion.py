"""
Script for marking for deletion, old package versions from a show on Shotgrid.
This script needs Launcher to be active, with a show selected, on the TD's/IT's workstation.

Script goes through ALL shots of the project, lists packages, 
and excludes packages found in the latest shot-definition.
After listing all old packages, it will export to the user's Desktop directory: 
 - a CSV file containing the packages info (id, entity type, path, name, size)
 - a TXT file containing the mains paths of the old packages.
Then create a batch update command per shot of the project, 
    to mark on SG per old package, True for 'sg_to_be_deleted'
"""
import os
import glob
import sys
import csv
import json
import shotgunlauncher
from studioshotgridapi import dbio
import argparse

# Args Parser
arg_description = '''Script for marking for deletion old packages in a shot(s) or all shots of a show.
                  Launch this script with your shotgunlauncher set to the project you're working on.'''
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=arg_description)
parser.add_argument("-s", "--shot_ids", type=lambda x:x.split(','),
                    help="Shot IDs to be queried on. If not used, queries ALL shots of the project")
parser.add_argument("-t", "--export_txt", action="store_true",
                    help="Exports the paths of old packages into a TXT file, on the user's Desktop")
parser.add_argument("-x", "--export_csv", action="store_true",
                    help="Exports the info of old packages into a CSV file, on the user's Desktop")
parser.add_argument("-m", "--mark_for_deletion", action="store_true",
                    help="Sets <sg_to_be_deleted> as TRUE for the old packages on the project, per shot")
args = parser.parse_args()
print(args)

# command to call `shotgun_api3.Shotgun()` directly.
current_config = shotgunlauncher.get_current_config()
sg_url = shotgunlauncher.get_shotgun_site_url()
db = dbio.DB(base_url=sg_url, 
             script_name='readonly', 
             api_key=[API_KEY])

project_id = int(current_config['project_id'])

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

def project_shot_list(project_id=project_id, shot_ids=[]):
    """
    Get all the project's shots.
    
    :param: project_id int: The Project ID number, found in
    :returns: shots List[Dict{shot}]: List of shots found through the SG query.
    """
    # Get Sequences
    filter_shots = [
        ['project', 'is', {'type': 'Project', 'id': int(project_id)}]
    ]
    fields_seq = ['code']
    order = [{'field_name': 'code', 'direction': 'asc'}]
    shots = db.sg.find(entity_type='Shot', filters=filter_shots, fields=fields_seq, order=order)

    print("Total Shots in show: {}".format(len(shots)))
    return shots

def get_shot_packages(shot_id):
    """
    :param shot_id int: the shot ID number 
    :returns: List[Dict{shot}]: List of shots found through the SG query.
    """
    # ALL SHOT PACKAGES 
    filters_package = [
        ['sg___package_type', 'in', ['anim-cache', 'layoutanim-cache', 'groom-ass']],
        ['sg___entity.Shot.id', 'is', shot_id]
    ]
    fields_package = ['id', 'code', 'sg___file_on_disk', 'sg___version_number', 'sg___package_type', 'sg___path', 'sg___task']
    order_package = [{'field_name': 'created_at', 'direction': 'desc'}]
    return db.sg.find(
        entity_type="CustomEntity01",
        filters=filters_package,
        fields=fields_package,
        order=order_package)

def get_packages_from_shot_definition(shot_definition_file):
    """
    Gets the cache packages from the shot-definition json file.
    :param: shot_definition_file str: path to the shot-definition file
    :returns: packages[{latest_package}] list[Dict{}]: list of packages from the Shot-Definition.
    """
    packages = []
    if shot_definition_file and os.path.exists(shot_definition_file) and shot_definition_file.endswith(".json"):
        # open json file from lightprep shot-definition
        with open(shot_definition_file) as json_file:
            data = json.load(json_file)    
            if "anim-cache" in data:
                for package_anim_cache in data["anim-cache"]:
                    packages.append(package_anim_cache["package_id"])
            if "grooms" in data:
                for package_grooms in data["grooms"]:
                    packages.append(package_grooms["package_id"])
    else:
        print("No shot-definition file provided, or file doesn't exist.", shot_definition_file)
    return packages

def create_txt_file(publish_data=None, file_name=''):
    """
    Creates a TXT file based on the publishes versions of the searched shots.

    :param list publish_data: The published versions data from the shots.
    """
    # Prepares file_name string
    file_name_str = ''
    for x in file_name:
        file_name_str += "_{}".format(int(x))

    # TXT file will be saved on user's Desktop.
    if not file_name:
        txt_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "old_packages_paths_proj{}.txt".format(project_id))
    else:
        txt_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "old_packages_paths_proj{}_shot{}.txt".format(project_id, file_name_str) )

    with open(txt_file, mode='wb') as t:
        progress_count = 0 # resets counter for progress bar
        for shot in publish_data:
            for data in shot:
                if "%04d" in data["sg___path"]: 
                    seq_files = glob.glob(data["sg___path"].replace("%04d","*"))
                    for file in seq_files:
                        t.write(file) # Path from file-sequence in 'shot' data
                        t.write('\n')
                else:
                    if os.path.exists(data["sg___path"]):
                        t.write(data["sg___path"]) # Path in 'shot' data
                        t.write('\n')
                    else:
                        print("TXT:", data["sg___path"], "cannot be found! Skipping.")
                        continue
            progress_count += 1 # counter for progress bar.
            progress(count=progress_count, total=len(publish_data), status="Writing to .TXT file")
        print("Finished writing to TXT file.\n")
                
def create_csv_file(publish_data=None, file_name=''):
    """
    Creates a CSV file based on the publishes versions of the searched shots.

    :param list publish_data: The published versions data from the shots.
    """
    # Prepares file_name string
    file_name_str = ''
    for x in file_name:
        file_name_str += "_{}".format(int(x))

    # CSV will be saved on user's Desktop.
    if not file_name:
        csv_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "old_packages_info_proj{}.csv".format(project_id))
    else:
        csv_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "old_packages_info_proj{}_shot{}.csv".format(project_id, file_name_str))
    fieldnames = [
        'id', 
        'code', 
        'sg___path', 
        'sg___version_number', 
        'sg___package_type', 
        'sg___task', 
        'sg___file_on_disk',
        'size',
        'type'
        ]

    with open(csv_file, mode='wb') as f:
        progress_count = 0 # resets counter for progress bar
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # write the header
        writer.writeheader()
        # write the rows of data
        for shot in publish_data:
            for data in shot:
                size = 0
                if "%04d" in data["sg___path"]:
                    seq_files = glob.glob(data["sg___path"].replace("%04d","*"))
                    for file in seq_files:
                        size += os.path.getsize(file)
                    data["size"] = size
                    writer.writerow(data)
                else:
                    if os.path.exists(data["sg___path"]):                   
                        size = os.path.getsize(data["sg___path"])
                        data["size"] = size
                        writer.writerow(data)
                    else:
                        print("CSV:", data["sg___path"], "cannot be found! Skipping.")
                        continue
            progress_count += 1 # counter for progress bar.
            progress(count=progress_count, total=len(publish_data), status="Writing to .CSV file")
        print("Finished writing to CSV file.\n")

def mark_packages_for_deletion(shot_packages=None):
    """
    Creates a ShotGrid batch command per shot, that includes the "update" commands for each package.

    :param shot_packages list[{dict}]: the list of multiple shot's packages dicts. [[shot{package}]]
    """
    progress_count = 0
    batch_data = []
    if shot_packages:
        # iterate through each shot of the project.
        for shot in shot_packages:
            # iterate through each package in shot.
            batch_data = [] # resets batch_data per shot
            for package in shot:
                update_data = {
                    "request_type": "update", 
                    "entity_type": "CustomEntity01", #entity_type is Package. 
                    "entity_id": int(package["id"]), 
                    "data": {"sg___to_be_deleted": True}
                    }
                batch_data.append(update_data)
            progress_count += 1    
            progress(count=progress_count, total=len(shot_packages), 
                     status="Marking packages for deletion \n")
            db.sg.batch(batch_data)


#_______________________________________________________________________________
# Gets the list of shots of the current show selected in Launcher.
# if args["shot_ids"]:
if args.shot_ids:
    # creates a list with dictionaries of provided shot_ids.
    shots = []
    for shot_id in args.shot_ids:
        shot = {}
        shot['id'] = int(shot_id)
        shots.append(shot)
else:
    shots = project_shot_list()

total_shot_packages_to_clean = []
progress_count = 0 # resets counter for progress bar

# Process gathering the latest shot-definition and packages per shot provided.
for shot in shots:
    progress_count += 1 # counter for progress bar.
    # grabs the latest shot definition
    latest_shot_definition = db.get_shot_definitions(
        project_id=project_id, shot_id=shot['id'], latest_version_only=True)
    if latest_shot_definition:
        # gets the latest packages from the shot-definition
        latest_packages = get_packages_from_shot_definition(
            shot_definition_file=latest_shot_definition['sg___path'])
    else:
        print("Error: Couldn't get the latest_shot_definition. Skipping shot")
        continue

    # gets the packages from the shot that needs to be sorted out.
    shot_packages = get_shot_packages(shot_id=shot['id'])

    shot_packages_to_clean = []
    # removes from the list of packages, the ones that are the latest versions.
    for package in shot_packages:
        if package["id"] not in latest_packages:
            shot_packages_to_clean.append(package)
        else:
            # Package is in shot-definition! Skipping it.
            continue
    # appends the old packages of the shot into a final list. Old packages grouped per shot.
    total_shot_packages_to_clean.append(shot_packages_to_clean)
    # progress bar
    if 'code' not in shot:
        progress(count=progress_count, total=len(shots), status="Done gathering {}.".format(shot["id"]))
    else:
        progress(count=progress_count, total=len(shots), status="Done gathering {}.".format(shot["code"]))

# create a CSV file containing old packages info, and a TXT file containing paths of old packages.
if args.export_txt:
    if args.shot_ids:
        create_txt_file(publish_data=total_shot_packages_to_clean, file_name=args.shot_ids)
    else:
        create_txt_file(publish_data=total_shot_packages_to_clean)
if args.export_csv:
    if args.shot_ids:
        create_csv_file(publish_data=total_shot_packages_to_clean, file_name=args.shot_ids)
    else:
        create_csv_file(publish_data=total_shot_packages_to_clean)
# mark found old packages, for deletion (attribute in SG: 'sg___to_be_deleted')
if args.mark_for_deletion:
    mark_packages_for_deletion(shot_packages=total_shot_packages_to_clean)

