import os
import sys
import subprocess


def fslash(path):
    """
    Replace backslashes with forward slashes in the given path.

    :param path: A string representing a file path.
    :return: A string with backslashes replaced by forward slashes.
    """
    return path.replace("\\", "/")

PLATFORM = sys.platform
PWD = os.path.dirname(os.path.abspath(__file__))
CIO_DIR = fslash(os.path.dirname(PWD))
print("CIO_DIR", CIO_DIR)

ADDOON_FILE = os.path.join(PWD, "conductor_submitter_plugin.py")
INIT_CONTENT = """
import sys
import os
CIO_DIR = '{}'
sys.path.insert(1, CIO_DIR)
os.environ['CIO_DIR'] = CIO_DIR
                       
from cioblender import conductor_submitter_plugin

bl_info = {{
    'name': 'Conductor Render Submitter',
    'author': 'Conductor Technologies, CoreWeave',
    'version': (0, 1, 7, 34),
    'blender': (4, 0, 1),
    'location': 'Render > Properties',
    'description': 'Conductor Render submitter UI',
    'category': 'Render',
}}

def register():
    conductor_submitter_plugin.register()

def unregister():
    conductor_submitter_plugin.unregister()

if __name__ == '__main__':
    register()
""".format(CIO_DIR)


def create_plugin_at_blender_folders(platform):
    """
    Copy the Conductor Blender plugin to Blender addon folders based on the platform.

    :param platform: The platform identifier (e.g., "win", "linux", "darwin").
    :return: A list of folders where the plugin was copied to.
    """
    user_home = os.path.expanduser("~")
    blender_versions_folder = None
    copied_folders = []
    addon_destination = ""

    if platform.startswith("win"):
        blender_versions_folder = os.path.join(user_home, "AppData/Roaming/Blender Foundation/Blender")
    elif platform.startswith("linux"):
        blender_versions_folder = os.path.join(user_home, ".config/blender")
    elif platform.startswith("darwin"):
        blender_versions_folder = os.path.join(user_home, "Library/Application Support/Blender")

    msg = "Source plugin: %s\n" % ADDOON_FILE
    sys.stdout.write(msg)
    if blender_versions_folder:
        for version_folder in os.listdir(blender_versions_folder):
            addon_folder = os.path.join(blender_versions_folder, version_folder, "scripts/addons")
            if not os.path.exists(addon_folder):
                try:
                    os.makedirs(addon_folder)
                except:
                    continue
            # Todo: Do we need to remove existing plugin file?
            """
            # Check and remove existing plugin file
            existing_plugin_path = os.path.join(addon_folder, "conductor.py")
            if os.path.exists(existing_plugin_path):
                try:
                    os.remove(existing_plugin_path)
                except Exception as e:
                    msg = "Unable to remove existing plugin at %s, error: %s\n" % (existing_plugin_path, e)
                    sys.stdout.write(msg)
            """
            # Write the new plugin
            try:
                addon_destination = os.path.join(addon_folder, "conductor.py")
                with open(addon_destination, "w", encoding="utf-8") as f:
                    f.write(INIT_CONTENT + "\n")

                copied_folders.append(addon_folder)
                msg = "Created Conductor Blender plugin %s\n" % addon_destination
                sys.stdout.write(msg)
            except Exception as e:
                sys.stderr.write(f"Unable to copy plugin {ADDOON_FILE} to folder {addon_destination}, error: {e}\n")

    return copied_folders

def remove_quarantine_attr(dir_path):
    """
    Remove the quarantine attribute from all files in the given directory recursively.

    :param dir_path: A string representing the path to the directory.
    """
    try:
        # Running the xattr command to remove the quarantine attribute
        subprocess.run(["xattr", "-dr", "com.apple.quarantine", dir_path], check=True)
        print(f"Quarantine removed from all files in {dir_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove quarantine from {dir_path}: {e}")

def remove_all_quarantine():

    # Paths to the shiboken6 and PySide6 directories in the parent directory
    shiboken6_dir = os.path.join(CIO_DIR, "shiboken6")
    pyside6_dir = os.path.join(CIO_DIR, "PySide6")

    # Remove quarantine from the directories
    remove_quarantine_attr(shiboken6_dir)
    remove_quarantine_attr(pyside6_dir)
def main():
    """
    Main function for setting up the Conductor Blender addon.

    This function adds the CIO_DIR path to the beginning of the addon file and copies the addon to Blender's
    addon folders based on the platform.
    """
    if not PLATFORM.startswith(("win", "linux", "darwin")):
        sys.stderr.write("Unsupported platform: {}\n".format(PLATFORM))
        sys.exit(1)

    # Remove all quarantine
    remove_all_quarantine()

    copied_folders = create_plugin_at_blender_folders(PLATFORM)

    if copied_folders:
        sys.stdout.write(f"Blender add-on setup successfully completed!\n")

    else:
        sys.stdout.write(f"Unable to locate any Blender add-on directories.\n")

if __name__ == "__main__":
    main()
