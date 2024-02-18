import os
import bpy
from cioblender import frames, util

RENDER_DICT = {
    "Cycles": "CYCLES",
    "Eevee": "BLENDER_EEVEE",
    # "Redshift": "REDSHIFT",
}


def get_task_template(**kwargs):
    """
    Generate a Blender command for rendering tasks.

    Args:
        kwargs (dict): A dictionary of keyword arguments for task configuration.

    Returns:
        str: The Blender command for rendering tasks.
    """
    first = kwargs.get("first", 1)
    last = kwargs.get("last", 1)
    step = kwargs.get("step", 1)

    render_filepath = get_render_file(kwargs)
    render_filepath = util.clean_and_strip_path(render_filepath)
    render_filepath = f'"{render_filepath}"'

    command_scene_path = render_filepath

    output_folder = kwargs.get("output_folder", None)
    output_folder = util.clean_and_strip_path(output_folder)
    # output_folder = f'"{output_folder}"'
    blender_filename = kwargs.get("blender_filename", None)
    if blender_filename:
        blender_filename = blender_filename.split(".")[0]

    output_path = os.path.join(output_folder, blender_filename)
    output_path = output_path.replace("\\", "/")
    output_path = "{}_".format(output_path)
    output_path = f'"{output_path}"'

    render_software = kwargs.get("render_software", None)
    render_software = RENDER_DICT.get(render_software, "CYCLES")
    render_software = f'"{render_software}"'

    cioblender_path = os.path.dirname(__file__)

    script_path = "{}/scripts/brender.py".format(cioblender_path)
    cio_dir = os.getenv('CIO_DIR')
    if cio_dir:
        script_path = "{}/cioblender/scripts/brender.py".format(cio_dir)

    script_path = util.clean_and_strip_path(script_path)
    script_path = f'"{script_path}"'

    instance_type = kwargs.get("instance_type", None)
    machine_type = kwargs.get("machine_type", None)

    resolution_x = kwargs.get("new_resolution_x", None)
    resolution_y = kwargs.get("new_resolution_y", None)

    camera = kwargs.get("camera_override", None)
    camera = f'"{camera}"'

    samples = kwargs.get("samples_override", None)
    extra_args = ""
    if resolution_x:
        extra_args += f" --resolution_x={resolution_x}"
    if resolution_y:
        extra_args += f" --resolution_y={resolution_y}"
    if camera:
        extra_args += f" --camera={camera}"
    if samples:
        extra_args += f" --samples={samples}"


    cmd = "blender -b {} -P {} -E {} --render-output {} -s {} -e {} -- render_device={} --machine_type={} {}".format(
       command_scene_path, script_path, render_software, output_path, first, last, instance_type, machine_type, extra_args)

    return cmd


def get_render_file(kwargs):
    """
    Save the current Blender file.

    Args:
        kwargs (dict): A dictionary of keyword arguments for task configuration.
    """
    render_filepath = None
    try:
        blender_filepath = kwargs.get("blender_filepath", None)
        render_filepath = blender_filepath

    except Exception as e:
        print("Error in saving render file {}, error: {}".format(render_filepath, e))
    return render_filepath


def resolve_payload(**kwargs):
    """
    Resolve the task_data field for the payload.

    If we are in sim mode, we emit one task.

    Args:
        kwargs (dict): A dictionary of keyword arguments for payload resolution.

    Returns:
        dict: A dictionary containing the task_data field for the payload.
    """

    tasks = []
    frame_info_dict = frames.set_frame_info_panel(**kwargs)
    kwargs["chunk_size"] = frame_info_dict.get("resolved_chunk_size")

    sequence = frames.main_frame_sequence(**kwargs)
    chunks = sequence.chunks()

    task_display_limit = kwargs.get("task_display_limit", False)
    display_tasks_count = len(chunks)
    if task_display_limit:
        display_tasks_count = kwargs.get("display_tasks", 1)
    # print("task_display_limit: {}".format(task_display_limit))
    # print("display_tasks_count: {}".format(display_tasks_count))
    # Get the scout sequence, if any.
    for i, chunk in enumerate(chunks):
        if task_display_limit:
            if i >= display_tasks_count:
                break
        # Get the frame range for this chunk.
        kwargs["first"] = chunk.start
        kwargs["last"] = chunk.end
        kwargs["step"] = chunk.step
        # Get the task template.
        cmd = get_task_template(**kwargs)

        tasks.append({"command": cmd, "frames": str(chunk)})


    return {"tasks_data": tasks}