"""
Script for listing latest asser versions packages.
This script needs studiolauncher to be active, with a show selected, on the TD's/IT's workstation.

Script goes through ALL shots of the project, lists packages, 
and excludes packages found in the latest shot-definition.
After listing all old packages, it will export to the user's Desktop directory: 
 - a CSV file containing the packages info (id, entity type, path, name, size)
 - a TXT file containing the mains paths of the old packages.
Then create a batch update command per shot of the project, 
    to mark on SG per old package, True for 'sg___to_be_deleted'
"""
import os
import glob
import sys
import csv
import json
import studiolauncher
from studioshotgrid import dbio
import argparse
import pprint
import operator

# Args Parser
arg_description = '''Script for marking for deletion old packages in a shot(s) or all shots of a show.
                  Launch this script with your studiolauncher set to the project you're working on.'''
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
                    help="Sets <sg___to_be_deleted> as TRUE for the old packages on the project, per shot")
args = parser.parse_args()
print(args)

# command to call `shotgun_api3.Shotgun()` directly.
current_config = studiolauncher.get_current_config()
sg_url = studiolauncher.get_shotgun_site_url()
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


def get_shot_packages(shot_id=None):
    """
    :param shot_id int: the shot ID number 
    :returns: List[Dict{shot}]: List of shots found through the SG query.
    """
    # ALL SHOT PACKAGES 
    filters = [
        ['sg___package_type', 'in', ['shot-definition', 'cameras-anim', 'groom-cache', 'layout-posinit', 'layout-anim']],
        ['sg___entity.Shot.id', 'is', shot_id]
    ]
    fields = ['id', 'code', 'description', 'sg___file_on_disk', 'sg___version_number', 'sg___package_type', 'sg___path', 'sg___task', 'sg___entity']
    order = [{'field_name':'sg___package_type', 'direction':'desc'}, {'field_name':'sg___task', 'direction':'desc'}, {'field_name':'sg___version_number', 'direction':'desc'}]
    return db.sg.find(
        entity_type="CustomEntity01",
        filters=filters,
        fields=fields,
        order=order)

def get_latest_shot_package(shot_id=None, type=None, codename=None):
    '''
    Returns a list of package of type provided
    '''
    fields = ['id', 'code', 'description', 'sg___file_on_disk', 'sg___version_number', 'sg___package_type', 'sg___path', 'sg___task', 'sg___entity']

    filters =   [
                ['sg___entity.Shot.id', 'is', int(shot_id)]
                ]
    
    order = [{'field_name': 'created_at', 'direction': 'desc'}]

    if shot_id != None:
        filters.append(['sg___entity', 'is', {'type': 'Shot', 'id' : int(shot_id)}])

    if type != None:
        filters.append(['sg___package_type', 'in', type])

    if codename != None:
        filters.append(['sg___filename', 'contains', codename])

    packages_list = db.sg.find("CustomEntity01", filters, fields)
    if packages_list != []:
        packages_list = max(packages_list, key=operator.itemgetter('sg___version_number'))
        return packages_list
    else:
        return None


def create_txt_file(publish_data=None, file_name=''):
    """
    Creates a TXT file based on the publishes versions of the searched shots.

    :param list publish_data: The published versions data from the shots.
    """
    # Prepares file_name string
    # file_name_str = ''
    # for x in file_name:
    #     file_name_str += "_{}".format(int(x))

    # TXT file will be saved on user's Desktop.
    if not file_name:
        txt_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "latest_packages_info_proj{}.txt".format(project_id))
    else:
        txt_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "latest_packages_info_proj{}_shot{}.txt".format(project_id, file_name) )

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
    # file_name_str = ''
    # for x in file_name:
    #     file_name_str += "_{}".format(int(x))

    # CSV will be saved on user's Desktop.
    if not file_name:
        csv_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "latest_packages_info_proj{}.csv".format(project_id))
    else:
        csv_file = os.path.join(os.environ["HOMEDRIVE"], 
                                os.environ["HOMEPATH"], 
                                "Desktop", 
                                "latest_packages_info_proj{}_shot{}.csv".format(project_id, file_name))
    fieldnames = [
        'id', 
        'code', 
        'sg___path', 
        'sg___version_number', 
        'sg___package_type', 
        'sg___task', 
        'size',
        'type',
        'description', 
        'created_at', 
        'sg___proxy', 
        'sg___branch',
        'sg___filename', 
        'sg_status_list',
        'sg___source_hash'
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



#_______________________________________________________________________________
# Gets the list of shots of the current show selected in studiolauncher.
# if args.shot_ids:
#     # creates a list with dictionaries of provided shot_ids.
#     # shots = []
#     shots = []
#     for shot_id in args.shot_ids:
#         shot = {}
#         shot['id'] = int(shot_id)
#         shots.append(shot)
# else:
#     shots = project_shot_list()
shots = []
# shot_ids = ['5396','4900']
shot_ids = ['2710']
for shot_id in shot_ids:                                                                                    
    shot = {}
    shot['id'] = int(shot_id)
    shots.append(shot)                                                                          
args.export_txt=False
args.export_csv=False
args.mark_for_deletion=False
args.shot_ids=shot_ids

total_latest_shot_packages = []
progress_count = 0 # resets counter for progress bar

# Process gathering the latest shot-definition and packages per shot provided.
for shot in shots:
    progress_count += 1 # counter for progress bar.
    # grabs the latest shot definition
    # latest_shot_definition = db.get_shot_definitions(
    #     project_id=project_id, shot_id=shot['id'], latest_version_only=True)
    # if latest_shot_definition:
    #     # gets the latest packages from the shot-definition
    #     latest_packages = get_packages_from_shot_definition(
    #         shot_definition_file=latest_shot_definition['sg___path'])
    # else:
    #     print("Error: Couldn't get the latest_shot_definition. Skipping shot")
    #     continue
    total_packages = []
    # shot_tasks = db.get_shot_tasks(project_id=project_id, shot_id=shot['id'])
    # print("\n======== shot tasks ==============")
    # pprint.pprint(shot_tasks)

    # Try to get the latest version of packages, by basing from the algorithm of ".get_published_files(except_latest_version)"

    # all_packages = db.get_all_shot_packages(project_id=project_id, shot_id=shot['id'])
    # pprint.pprint(packages)
    all_non_cache_packages = get_shot_packages(shot_id=shot['id'])
    print("\n =============== all_non_cache_packages =============")
    # pprint.pprint(all_non_cache_packages)
    for p in all_non_cache_packages:
        print(p['code'], p['sg___version_number'], p['sg___package_type'], p['sg___task'])

    # get names
    codenames = set()
    # version = dict(
    #     "name"
    # )
    for package in all_non_cache_packages:
        name = package['code'].split(".")
        print(name)
        # codenames.add("{}.{}".format(name[0], name[-1]))
        codenames.add("{}".format(name[0]))
    pprint.pprint(codenames)

    types = ['shot-definition', 'cameras-anim', 'groom-cache', 'layout-posinit', 'layout-anim']
    total_latest = []
    
    for codename in codenames:
        # for type in types:
        latest_version = get_latest_shot_package(
            shot_id=shot_id,
            type=types,
            codename="{0}".format(codename))
        if latest_version:
            print("latest_version = ", latest_version['code'])
            total_latest.append(latest_version)
    
    pprint.pprint(total_latest)
    if package['code'].split(".")[0] in codenames:
        print("name is inside codenames")
        total_latest.append(package)

    # print("\n====== all_non_cache_packages ======")
    # pprint.pprint(all_non_cache_packages)

    # get all types of packages in shot
    # sorted(all_non_cache_packages, key=operator.itemgetter('sg___version_number'))
    # package_types = set()
    # for package in all_non_cache_packages:



    # Get latest versions only (?)
    # for package in all_non_cache_packages:
        # latest_version = db.get_packages(project_id=project_id, 
        #                                 type=package['sg___package_type'],
        #                                 task_id=package['sg___task']['id'])
        # print("latest version: ", latest_version['code'], latest_version['sg___version_number'])
        # total_latest.append(latest_version)



    # total_latest_shot_packages.append(latest_packages)
    
    # Totals the shot packages


    # progress bar
    if 'code' not in shot:
        progress(count=progress_count, total=len(shots), status="Done gathering {}.".format(shot["id"]))
    else:
        progress(count=progress_count, total=len(shots), status="Done gathering {}.".format(shot["code"]))

# create a CSV file containing old packages info, and a TXT file containing paths of old packages.
if args.export_txt:
    if args.shot_ids and len(args.shot_ids) >= 2:
        create_txt_file(publish_data=total_packages, file_name="{0}_{1}".format(args.shot_ids[0],args.shot_ids[-1]))
    elif args.shot_ids and len(args.shot_ids) == 1:
        create_txt_file(publish_data=total_packages, file_name=args.shot_ids)
    else:
        create_txt_file(publish_data=total_packages)
if args.export_csv:
    if args.shot_ids and len(args.shot_ids) >= 2:
        create_csv_file(publish_data=total_packages, file_name="{0}_{1}".format(args.shot_ids[0],args.shot_ids[-1]))
    elif args.shot_ids and len(args.shot_ids) == 1:
        create_csv_file(publish_data=total_packages, file_name=args.shot_ids)
    else:
        create_csv_file(publish_data=total_packages)
