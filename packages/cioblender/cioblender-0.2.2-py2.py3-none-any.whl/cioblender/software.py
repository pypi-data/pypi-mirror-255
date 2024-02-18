

from ciocore import data as coredata
from cioblender import driver


def populate_host_menu():
    """
    Populate Blender version menu.

    This function is called by the UI whenever the user clicks the Blender Version button.

    Returns:
        list of str: A list of supported Blender versions.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    if not host_names:
        return [("no_host_names", "-- No hostnames --", "")]
    else:
        # Create a dictionary of projects
        blender_host_names = {}
        # For each host in the host_names, if the host is not in the blender_host_names dictionary,
        # add it to the dictionary
        for s in host_names:
            if s not in blender_host_names:
                blender_host_names[s] = (s, s, "")
        # Return the list of hosts
        return list(blender_host_names.values())


def populate_driver_menu(**kwargs):
    """
    Populate the renderer/driver type menu.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        list of str: A list of driver types.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]
    print("Driver menu: ")
    print ([el for i in _get_compatible_plugin_versions(**kwargs) for el in (i,i)])

    return [el for i in _get_compatible_plugin_versions(**kwargs) for el in (i,i)]



def _get_compatible_plugin_versions(**kwargs):
    """
    Get compatible plugin versions.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        list of str: A list of compatible plugin versions.
    """
    driver_data = driver.get_driver_data(**kwargs)
    if driver_data["conductor_product"].lower().startswith(("built-in", "unknown")):
        return [driver_data["conductor_product"]]

    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    print("software_data: {}".format(software_data))
    selected_host = kwargs.get("blender_version")
    print("selected_host: {}".format(selected_host))
    plugins = software_data.supported_plugins(selected_host)
    print("plugins: {}".format(plugins))
    plugin_names = [plugin["plugin"] for plugin in plugins]
    print("plugin_names: {}".format(plugin_names))

    if driver_data["conductor_product"] not in plugin_names:
        return ["No plugins available for {}".format(driver_data["conductor_product"])]

    plugin_versions = []
    for plugin in plugins:
        if plugin["plugin"] == driver_data["conductor_product"]:
            for version in plugin["versions"]:
                plugin_versions.append("{} {}".format(
                    plugin["plugin"], version))
            break
    print("plugin_versions: {}".format(plugin_versions))
    
    return plugin_versions


def resolve_payload(**kwargs):
    """
    Resolve the package IDs section of the payload for the given node.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the resolved package IDs.
    """
    ids = set()

    for package in packages_in_use(**kwargs):
        ids.add(package["package_id"])

    return {"software_package_ids": list(ids)}

def packages_in_use(**kwargs):
    """
    Return a list of packages as specified by names in the software dropdowns.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        list of dict: A list of packages.
    """
    if not coredata.valid():
        return []
    tree_data = coredata.data().get("software")
    #print("tree_data: {}".format(tree_data))
    if not tree_data:
        return []

    platform = list(coredata.platforms())[0]
    host = kwargs.get("blender_version")
    blender_version = kwargs.get("blender_version")
    driver = "{}/{} {}".format(host, blender_version, platform)
    paths = [host, driver]
    num_plugins = kwargs.get("extra_plugins", 0)
    for i in range(1, num_plugins+1):
        parm_val = kwargs["extra_plugin_{}".format(i)]
        paths.append("{}/{} {}".format(host, parm_val, platform))

    return list(filter(None, [tree_data.find_by_path(path) for path in paths if path]))





