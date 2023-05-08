# Validators written for Animation Validation system/Sanity Checker, before exporting/publishing shots or assets

class AnimationGeometryCacheValidator(<MainAnimationValidator>):
    """
    Validator to check if geometry cache is present on disk and in scene.
    Geometry Caches should be removed before publishing.
    """
    def validate(self):
        """
        Validates if each slot about to be published, has geometry cache. If yes, the slot it's added to error list.

        :return: List of errors detected.
        :rtype: list[<studio.validate>.ValidationError]
        """
        errors = []
        slots_with_cache = []

        title = "Animation Cache present in scene."
        error_msg = "There is Geometry Cache present in scene, for the following slots:\n"

        cache_nodes = return_geometry_cache_nodes(slots=self.bundle_slot_names)
        print(cache_nodes)
        if cache_nodes:
            for slot in self.<studio-package-slot-names>:
                if check_for_cache_files(slots=[slot]):
                    error_msg += "{0} \n".format(slot)
                    slots_with_cache.append(slot)
            if slots_with_cache:
                error_msg += "Nodes: {0}".format(cache_nodes)
                errors.append(self.new_warning(title, error_msg, error_data=slots_with_cache, is_fixable=True))
                return errors

    def fix(self, error):
        """
        Fixes the error, by removing the geometry cache of the slot in case.

        :param <studio.validate>.ValidationError error: The flagged error
        """
        slots_with_cache = error.error_data
        for slot in slots_with_cache:
            delete_cache_file(cache_name="{0}_face_rig_geometry_cache".format(slot))


class CameraNameValidator(<MainAnimationValidator>):
    """
    Class for validating camera name.
    """
    def validate(self):
        """
        Check if required camera is named correctly as
        camera once the namespace is removed.
        :rtype: list[<studio.validate>.ValidationError]
        """
        errors = list()
        for container in <package_container.PackageContainerClass>.find_all(publishable=True, skip_empty=True):
            cameras = container.container_node.getChildren(allDescendents=True, type='camera')
            if len(cameras) == 1:
                camera_trans_name = cameras[0].getParent().name()
                basename = camera_trans_name.split(':')[-1]
                if basename != 'camera':
                    correct_name = '%scamera' % container.container_node.namespace()
                    msg = '"%s" should be named "%s"' % (camera_trans_name, correct_name)
                    errors.append(self.new_error('Camera named incorrectly', msg,
                                                 error_data=[camera_trans_name, correct_name], is_fixable=True))
        return errors

    def fix(self, error):
        camera_trans_name, correct_name = error.error_data
        pm.rename(camera_trans_name, correct_name)
		
		
		
class NonReferencedGeometryValidator(<MainAnimationValidator>):
    """
    Validates if there are non-referenced geometries under a referenced container
     different than NonReferencedNodesValidator, because it confirms the transform of the non-reference mesh in not
     referenced which is important because the NonReferencedNodesValidator, was finding in-shot deformed meshes
    """

    def validate(self):
        errors = list()

        meshes_to_fix = []
        for slot_name in self.slot_names:
            container = <package_container.PackageContainerClass>.find_container(slot_name)
            if not container:
                continue

            logger.info("Looking for non-referenced deformed meshes in scene".format(slot_name))
            meshes = container.container_node.listRelatives(ad=1, type='shape')
            for mesh in meshes:
                if not mesh.isReferenced() and not mesh.getParent().isReferenced():
                    meshes_to_fix.append(mesh.getParent().longName())

        if meshes_to_fix:
            title = "Non-Referenced Geometry Transforms under References"
            msg = ("Please fix this issue so imported meshes don't get exported"
                   "\nThe issued geometry are:\n {}").format('\n'.join(meshes_to_fix))
            errors.append(self.new_error(title, msg, meshes_to_fix, is_fixable=False))

        return errors
