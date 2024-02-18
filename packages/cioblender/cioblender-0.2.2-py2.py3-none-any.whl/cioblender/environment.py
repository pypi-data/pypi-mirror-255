
from cioblender import software, util

def resolve_payload(**kwargs):
    """
    Resolve the payload for the environment.

    This function retrieves and processes environment information, including the 'PATH' variable and additional
    environment variables, based on the provided keyword arguments. It compiles the relevant environment variables
    into a dictionary and returns it as part of the payload.

    :param kwargs: A dictionary of keyword arguments that may include 'extra_variables'.
    :return: A dictionary containing the 'environment' key with the environment variables.
    """

    # Get unique paths from packages with non-empty 'path' attribute
    paths = list({package.get("path") for package in software.packages_in_use(**kwargs) if package.get("path")})

    # Join the unique paths with ":"
    blender_path = ":".join(paths)

    # Define a dictionary for environment variables
    env_dict = {
        "PATH": blender_path,
    }
    try:
        extra_variables = kwargs.get("extra_variables", None)

        if extra_variables:
            for variable in extra_variables:
                key, value = variable.variable_name, variable.variable_value
                if key and value:
                    env_dict[key] = value
    except Exception as e:
        print ("Unable to get extra environment variables. Error: {}".format(e))
        pass


    return {"environment": env_dict}