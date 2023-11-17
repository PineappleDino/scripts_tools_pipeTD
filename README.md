# scripts_tools_pipeTD
My scripts and tools done at VFX/Animation studios, for workflow and pipeline purposes.
(NOTE: those scripts were implemented with the studios' major APIs and libraries, so they may not work as intended when used directly here as they are. Year when created are mentioned).


## ATD_ScriptChallenge.py (2018)
Script challenge attempted, created by senior ATDs in one of the studios.

## ATD_elementList_forAnim.py (2018)
Tool for populating elementing lists for animation-task shots.

## Create_BlendshapeSet (2022)
Maya Shelf button for creating an ObjectSet for a selected animation rig, where it adds the basic body geometry, needed to extract blendshapes from a published Animation clip.

## DeleteCameraCropMask.py (2018)
Tiny script for deleting cropmask from camera asset objects.

## Export_template_fx_VDB_nodes.py (2023)
Export template for FX assets in FX tasks (Maya) based on studio's base export template. Allowed to export imported VDBs in Maya, to publish to Shotgrid.

## FilesRenamer_withGUI.py (2018)
Little file renaming tool, to try out different styling options of PyQt.

## Geo_and_UV_duplicateSpecial.py (2018)
Maya tool for moving/rotating Geometry UVmaps

## ImageRef_Loader_for_Maya.py (2018)
Maya tool for loading a picture into a plane geo, into the scene. Requested by modelling departments.

## Validators_for_animation.py (2020)
Maya Animation validators written for studio's validator system, for animation shot tasks.

## clean_old_caches_and_mark_for_deletion.py (2023)
Terminal python program to delete old generated caches from animation and crowd publishes, listed in shotgrid.

## facial_cache_geometry.py (2022)
Maya tool to create geometry cache of characters facial proxies, so that animators could disable head and face controls after facial animation was done. Disabling facial rigging and controllers keyframes would improve maya performance.

## import_golaem_caches.py (2023)
Maya tool for import golaem cache files from another shot's maya workspace, into the current one.

## list_latest_version.py (2023)
Terminal Python program to list and export, in a CSV file, old asset versions based on a latest shot-definition file's from the show in Shotgrid.
