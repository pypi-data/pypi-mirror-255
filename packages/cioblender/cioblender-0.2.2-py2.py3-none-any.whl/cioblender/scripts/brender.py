import bpy
import sys

import logging
logger = logging.getLogger(__name__)


def get_custom_arg(key, default_value=None):
    try:
        idx = sys.argv.index("--") + 1
        for arg in sys.argv[idx:]:
            if arg.startswith(key) or arg.startswith(f"--{key}"):
                value = arg.split('=')[1]
                print(f"Found argument {key}: {value}", flush=True)
                return value
    except (ValueError, IndexError):
        pass
    return default_value

def get_basic_arg(key, default_value=None):
    try:
        idx = sys.argv.index("-P") + 1
        args = sys.argv[idx:]
        # print("args:", args, flush=True)
        if key in ['-E', '-s', '-e', '--render-output']:
            # Special handling for start frame, end frame, and render output folder
            for i, arg in enumerate(args):
                # print("i:", i, "arg:", arg, flush=True)
                if arg == key:
                    return args[i + 1]  # Return the value following the key
        else:
            # For other keys, assume the format is 'key=value'
            for arg in args:
                if arg.startswith(key):
                    return arg.split('=')[1]
    except (ValueError, IndexError):
        pass
    return default_value

def load_file():
    # Open the .blend file we will be working with
    filepath = None
    try:
        filepath = bpy.data.filepath
        print("filepath:", filepath, flush=True)
        bpy.ops.wm.open_mainfile(filepath=filepath)
    except RuntimeError:
        logger.error("Unable to open file: {}".format(filepath))
        raise

def setup_format(scene):
    if scene.render.image_settings.file_format in ['FFMPEG', 'AVI_JPEG', 'AVI_RAW']:
        scene.render.image_settings.file_format = 'PNG'


def setup_camera(scene):
    camera_name = get_custom_arg("--camera", None)
    if camera_name:
        try:
            print("Setting camera to: {}".format(camera_name), flush=True)
            scene.camera = bpy.data.objects[camera_name]

        except KeyError:
            logger.error(f"Camera {camera_name} not found in scene {scene.name}")
            raise

def setup_resolution(scene):
    resolution_x = get_custom_arg("--resolution_x", None)
    if resolution_x:
        resolution_x = int(resolution_x)
        if resolution_x > 0:
            print("Setting Resolution X to: {}".format(resolution_x), flush=True)
            scene.render.resolution_x = resolution_x

    resolution_y = get_custom_arg("--resolution_y", None)
    if resolution_y:
        resolution_y = int(resolution_y)
        if resolution_y > 0:
            print("Setting Resolution Y to: {}".format(resolution_y), flush=True)
            scene.render.resolution_y = resolution_y

    # Set the resolution percentage to 100% to avoid scaling the output
    # resolution_x and resolution_y are already set to the desired values
    scene.render.resolution_percentage = 100


def setup_samples(scene):
    samples = get_custom_arg("--samples", None)
    if not samples:
        return
    samples = int(samples)

    # Renderer that is currently set in the scene and used here as default
    scene_render_software = scene.render.engine.lower()
    # render software that was passed in as an argument
    render_software = get_basic_arg("-E", scene_render_software)

    # Override the samples if the user has passed in a value
    if samples and samples > 0:
        if render_software.lower() == "cycles":
            print("Setting samples to: {}".format(samples), flush=True)
            scene.cycles.samples = samples
        elif render_software.lower() == "eevee":
            print("Setting samples to: {}".format(samples), flush=True)
            scene.eevee.taa_render_samples = samples
        #elif render_software.lower() == "redshift":
        #    # Todo: Assuming Redshift uses a 'samples' property, modify as needed
        #    scene.redshift.RenderOptions.max_samples = samples
def set_tile_size(scene):
    try:
        blender_version = bpy.app.version
        # print("Blender version: {}".format(blender_version), flush=True)
        scene_render_software = scene.render.engine.lower()
        render_software = get_basic_arg("-E", scene_render_software)
        print("Render software: {}".format(render_software), flush=True)
        if render_software.lower() == "cycles":
            if blender_version < (3, 0, 0):
                scene.render.tile_x = min(scene.render.tile_x, 128)
                scene.render.tile_y = min(scene.render.tile_y, 128)
                scene.cycles.tile_order = 'RIGHT_TO_LEFT'
                print("Setting tile size to: {}x{}".format(scene.render.tile_x, scene.render.tile_y), flush=True)
            else:
                # Enforce minimum tile sizing for >= 3.0
                scene.cycles.tile_size = max(scene.cycles.tile_size, 128)
                print("Setting tile size to: {}".format(scene.cycles.tile_size), flush=True)
    except Exception as e:
        logger.debug("Error setting tile size, {}", e)


def render_type(scene):
    instance_type = get_custom_arg("render_device", "GPU")
    instance_type = instance_type.lower()
    if instance_type == "gpu":
        scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.device = 'GPU'
        msg = "Setting rendering device to GPU"
        print(msg, flush=True)
        preferences = bpy.context.preferences.addons['cycles'].preferences
        for device_type in preferences.get_device_types(bpy.context):
            preferences.get_devices_for_type(device_type[0])
        # Enable all available GPUs
        msg = "Enabling all available CUDA GPUs"
        print(msg, flush=True)
        logger.info(msg)
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'


        for d in preferences.devices:
            if d.type == 'CPU':
                print('Disabling Device {} of type {}'.format(d.name, d.type), flush=True)
                d.use = False
            # GPU
            else:
                # Todo: check if this is needed
                # if d.type in ['CUDA', 'OPTIX']:
                print('Enabling Device {} of type {}'.format(d.name, d.type), flush=True)
                d.use = True

    else:
        """
        threads
        Maximum number of CPU cores to use simultaneously while rendering (for multi-core/CPU systems)
        Type
        int in [1, 1024], default 1
        threads_mode
        Determine the amount of render threads used
        AUTO Auto-Detect – Automatically determine the number of threads, based on CPUs.
        FIXED Fixed – Manually determine the number of threads.
        Type
        enum in [‘AUTO’, ‘FIXED’], default ‘AUTO’
        """
        msg = "Setting rendering device to CPU"
        print(msg, flush=True)
        thread_count = get_thread_count()
        print("Thread count: {}".format(thread_count), flush=True)
        if thread_count > 1:
            scene.render.threads_mode = 'FIXED'
            scene.render.threads = thread_count
            msg = "Setting threads mode to {} and render threads to {}".format(scene.render.threads_mode, thread_count)
            print(msg, flush=True)
            logger.info(msg)
        else:
            scene.render.threads_mode = 'AUTO'
            msg = "Setting threads mode to {}".format(scene.render.threads_mode)
            print(msg, flush=True)
            logger.info(msg)


def extra_settings(scene):
    # Force turn off progressive refine, since we are not in viewport
    bpy.context.scene.cycles.use_progressive_refine = False
    # Disable placeholder frame files
    bpy.context.scene.render.use_placeholder = False
    # Force file output to have a file extension
    bpy.context.scene.render.use_file_extension = True
    # Enable overwrite prompt
    bpy.context.scene.render.use_overwrite = True

def setup_redshift(scene):
    scene_render_software = scene.render.engine.lower() # cycles, eevee, redshift
    render_software = get_basic_arg("-E", scene_render_software)
    print("Render software: {}".format(render_software), flush=True)
    if render_software.lower() == "redshift":
        # Enable Redshift addon
        #bpy.context.preferences.addons["redshift"].preferences.is_gpu_enabled = True
        #bpy.context.preferences.addons["redshift"].preferences.is_cpu_enabled = False
        #bpy.context.preferences.addons["redshift"].preferences.is_hybrid_enabled = False
        # Enable Redshift renderer
        #scene.render.engine = 'REDSHIFT'
        # Enable Redshift device
        scene.render.engine = 'RED_SHIFT'
        print("Setting rendering device to RED_SHIFT", flush=True)
        print("Scene render engine is {}".format(bpy.context.scene.render.engine))

        try:
            from redshift import preferences
            import rs_python


            redshift_addon_devices = bpy.context.preferences.addons["redshift"].preferences.devices
            devices = preferences.getAllDevices()
            gpus = []
            for device_idx in range(devices.Length()):
                gpus.append(rs_python.intp_value(devices[device_idx]))

                for device in preferences.getAllComputeDevices():
                    device_data = device.split(sep=':')
                    entry = [d for d in redshift_addon_devices if d.id == device_data[0]]
                    if not entry:
                        entry = redshift_addon_devices.add()
                        entry.id = device_data[0]
                        entry.name = device_data[1]
                        entry.use = True

                    selectedDevices = ','.join(preferences.getAllComputeDevices()) + ','

                    bpy.context.preferences.addons["redshift"].preferences.HybridRendering = True
                    rs_python.RS_Renderer_SetPreferenceValue("SelectedComputeDevices", selectedDevices, True)
                    rs_python.RS_Renderer_SetPreferenceValue("HybridRendering", 1, True)
        except Exception as e:
            logger.debug("Unable to setup redshift, error: {}".format(e))

def get_thread_count():

    thread_count = 1
    try:
        machine_type = get_custom_arg("--machine_type", None)
        print("Machine type: {}".format(machine_type), flush=True)
        if machine_type:
            thread_count = machine_type.split("-")[-1]
            print("Thread count: {}".format(thread_count), flush=True)
            return int(thread_count)
    except Exception as e:
        logger.debug("Unable to get machine type, error: {}".format(e))
    return thread_count


def setup_renderer(scene):
    setup_format(scene)
    setup_camera(scene)
    setup_resolution(scene)
    setup_samples(scene)
    set_tile_size(scene)
    render_type(scene)
    # setup_redshift(scene)
    extra_settings(scene)


def enable_addons():
    try:
        bpy.ops.preferences.addon_enable(module="render_auto_tile_size")
    except Exception as e:
        logger.debug("Unable to enable plugin render_auto_tile_size, error: {}".format(e))

    # bpy.context.scene.ats_settings.is_enabled = True

def do_render(scene):
    output_folder = get_basic_arg('--render-output', default_value="")
    bpy.context.scene.render.filepath = output_folder

    # Get start and end frames from command line arguments
    start_frame = int(get_basic_arg('-s', default_value="1"))
    end_frame = int(get_basic_arg('-e', default_value="1"))

    # Handle animation rendering for the specified frame range
    for frame in range(start_frame, end_frame + 1):
        print("Rendering frame {}".format(frame), flush=True)
        scene.frame_set(frame)
        # Update the file path for each frame using the provided output directory
        scene.render.filepath = f'{output_folder}{frame:04d}'
        bpy.ops.render.render(write_still=True, use_viewport=False, layer="")


def run():
    load_file()
    scene = bpy.context.scene
    setup_renderer(scene)
    # TODO: Enable addons, and add support for all addons
    # enable_addons()
    do_render(scene)
# Main
if __name__ == '__main__':
    run()
