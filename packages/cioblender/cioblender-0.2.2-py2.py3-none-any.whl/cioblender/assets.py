import bpy
import os
from ciopath.gpath_list import PathList, GLOBBABLE_REGEX
import logging
from cioblender import task, util

logger = logging.getLogger(__name__)

STARTUP_VAL = "startup.blend"

def resolve_payload(**kwargs):
    """
    Resolve the upload_paths field for the payload.

    This function gathers a list of file paths to be uploaded, including auxiliary paths,
    extra assets, and scanned assets, and returns them as a dictionary.

    :param kwargs: A dictionary of keyword arguments that may include "blender_filepath".
    :return: A dictionary containing the "upload_paths" key with a list of file paths.
    """
    path_list = PathList()

    path_list.add(*auxiliary_paths(**kwargs))
    path_list.add(*extra_paths())
    path_list.add(*scan_assets())

    return {"upload_paths": [p.fslash() for p in path_list]}


def resolve_payload_extended(**kwargs):
    """
    Resolve the upload_paths field for the payload.

    This function gathers a list of file paths to be uploaded, including auxiliary paths,
    extra assets, and scanned assets, and returns them as a dictionary.

    :param kwargs: A dictionary of keyword arguments that may include "blender_filepath".
    :return: A dictionary containing the "upload_paths" key with a list of file paths.
    """
    path_list = PathList()

    path_list.add(*auxiliary_paths(**kwargs))
    path_list.add(*extra_paths())
    path_list.add(*scan_assets())

    try:
        blender_folder = None

        output_folder = kwargs.get("output_folder", None)
        if output_folder:
            output_folder = output_folder.replace("\\", "/")
        blender_filepath = kwargs.get("blender_filepath")
        if blender_filepath:
            blender_filepath = blender_filepath.replace("\\", "/")
            blender_folder = os.path.dirname(blender_filepath)
        # print("blender_folder : {}".format(blender_folder))
        # print("output_folder : {}".format(output_folder))

        # Get the current assets
        current_assets = []
        for path in path_list:
            path = str(path)
            path = path.replace("\\", "/")
            if path not in current_assets:
                current_assets.append(str(path))

        # print("Updated current assets: {}".format(current_assets))
        # Filter out paths that are within the output folder
        # Todo: Add a validation warning for this
        filtered_paths = [path for path in current_assets if not is_within_output_folder(path, output_folder)]
        # print("filtered paths before removing the blender folder: {}".format(filtered_paths))
        # Filter out paths that are the "blender file folder"
        filtered_paths = [path for path in filtered_paths if not path == blender_folder]
        # print("filtered paths after removing the blender folder: {}".format(filtered_paths))
        return {"upload_paths": filtered_paths}

    except Exception as e:
        logger.debug("Unable to clean assets, error: {}".format(e))

    return {"upload_paths": [p.fslash() for p in path_list]}

def is_within_output_folder(path, output_folder):
    # Normalize the paths to handle different platforms and spaces
    normalized_path = os.path.normpath(str(path))  # Convert path to string
    normalized_output_folder = os.path.normpath(str(output_folder))  # Convert path to string

    # Check if the normalized path is within the normalized output folder
    result = normalized_path.startswith(normalized_output_folder)
    return result

def auxiliary_paths(**kwargs):
    """
    Get auxiliary paths.

    This function retrieves auxiliary paths, specifically the "blender_filepath" if it exists.

    :param kwargs: A dictionary of keyword arguments that may include "blender_filepath".
    :return: A PathList object containing auxiliary paths.
    """
    path_list = PathList()
    """
    try:
        blender_filepath = kwargs.get("blender_filepath")
        blender_filepath = blender_filepath.replace("\\", "/")
        if blender_filepath and STARTUP_VAL not in blender_filepath:
            # Check if blender_filepath exists
            if os.path.exists(blender_filepath):
                path_list.add(blender_filepath)
                path_list.real_files()
            else:
                logger.debug("Unable to find blender_filepath: {}".format(blender_filepath))
    except Exception as e:
        logger.debug("Unable to load blender_filepath, error: {}".format(e))
    """


    try:
        blender_filepath = kwargs.get("blender_filepath")
        blender_filepath = blender_filepath.replace("\\", "/")
        render_filepath = task.get_render_file(kwargs)
        if render_filepath:
            render_filepath = render_filepath.replace("\\", "/")
            # Check if render_filepath exists
            if os.path.exists(render_filepath):
                path_list.add(render_filepath)
                path_list.real_files()
            else:
                logger.debug("Unable to find blender_filepath: {}".format(blender_filepath))
    except Exception as e:
        logger.debug("Unable to load blender_filepath, error: {}".format(e))

    try:
        cio_dir = os.getenv('CIO_DIR')
        if cio_dir:
            script_path = "{}/cioblender/scripts/brender.py".format(cio_dir)
            if os.path.exists(script_path):
                path_list.add(script_path)
    except Exception as e:
        logger.debug("Unable to load script_path, error: {}".format(e))


    return path_list

def extra_paths():
    """
    Add extra assets.

    This function retrieves extra assets from the current Blender scene and adds them to the PathList.

    :return: A PathList object containing extra asset paths.
    """
    path_list = PathList()
    try:
        scene = bpy.context.scene
        extra_assets_list = scene.extra_assets_list

        for asset in extra_assets_list:
            if asset.file_path and STARTUP_VAL not in asset.file_path:
                # Check if asset.file_path exists
                if os.path.exists(asset.file_path):
                    path_list.add(asset.file_path)
                    path_list.real_files()
                else:
                    logger.debug("Unable to find extra asset: {}".format(asset.file_path))
    except Exception as e:
        logger.debug("Unable to load extra assets, error: {}".format(e))

    return path_list

def scan_assets():
    """
    Scan assets in the current Blender project and return a PathList containing their paths.

    :return: A PathList object containing the paths of scanned assets.
    """
    path_list = PathList()

    path_list.add(*scan_materials())
    path_list.add(*scan_objects())
    path_list.add(*scan_linked_libraries())
    path_list.add(*scan_objects_with_overrides())

    return path_list

def scan_materials():
    """
    Scan materials in the current Blender project and add their image paths to the PathList.

    :return: A PathList object containing image paths from materials with nodes.
    """
    path_list = PathList()
    try:
        if not bpy.data.materials:
            return path_list
        # Iterate through all materials in the scene
        for material in bpy.data.materials:
            if not material.use_nodes:
                continue
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    image_filepath = bpy.path.abspath(node.image.filepath)
                    # check if the image_filepath exists
                    if os.path.exists(image_filepath):
                        path_list.add(image_filepath)
                        path_list.real_files()
                    else:
                        logger.debug("Unable to find image_filepath: {}".format(image_filepath))
    except Exception as e:
        logger.debug("Unable to scan materials, error: {}".format(e))

    return path_list

def scan_objects():
    """
    Scan objects in the current Blender project and add image paths from materials with nodes to the PathList.

    :return: A PathList object containing image paths from materials in mesh objects.
    """
    path_list = PathList()

    try:
        if not bpy.data.objects:
            return path_list
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if not slot.material:
                        continue
                    if slot.material and slot.material.use_nodes:
                        for node in slot.material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image:
                                image_filepath = bpy.path.abspath(node.image.filepath)
                                # check if the image_filepath exists
                                if os.path.exists(image_filepath):
                                    path_list.add(image_filepath)
                                    path_list.real_files()
                                else:
                                    logger.debug("Unable to find image_filepath: {}".format(image_filepath))
    except Exception as e:
        logger.debug("Unable to scan objects, error: {}".format(e))
    return path_list

def scan_linked_libraries():
    """
    Scan linked libraries in the current Blender project and add their paths to the PathList.

    :return: A PathList object containing paths of linked libraries.
    """
    path_list = PathList()

    try:
        if not bpy.data.libraries:
            return path_list
        for library in bpy.data.libraries:
            # Check if the library is linked or used in the scene
            if library.users > 0:
                library_filepath = bpy.path.abspath(library.filepath)
                # check if the library_filepath exists
                if os.path.exists(library_filepath):
                    path_list.add(library_filepath)
                    path_list.real_files()
                else:
                    logger.debug("Unable to find linked library: {}".format(library_filepath))
    except Exception as e:
        logger.debug("Unable to scan linked libraries, error: {}".format(e))
    return path_list

def scan_objects_with_overrides():
    """
    Scan objects with library overrides and add material library paths to the PathList.

    :return: A PathList object containing material library paths of objects with overrides.
    """
    path_list = PathList()

    try:
        if not bpy.context.scene.objects:
            return path_list
        for obj in bpy.context.scene.objects:
            if obj.is_library_indirect:
                for slot in obj.material_slots:
                    if not slot.material:
                        continue
                    material_filepath = bpy.path.abspath(slot.material.library.filepath)
                    # check if the material_filepath exists
                    if os.path.exists(material_filepath):
                        path_list.add(material_filepath)
                        path_list.real_files()
                    else:
                        logger.debug("Unable to find object with override: {}".format(material_filepath))
    except Exception as e:
        logger.debug("Unable to scan objects with overrides, error: {}".format(e))
    return path_list

