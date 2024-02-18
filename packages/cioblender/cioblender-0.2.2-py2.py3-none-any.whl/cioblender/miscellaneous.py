
def resolve_payload(**kwargs):
    """
    Resolve the notifications field for the payload.

    This function sets the 'local_upload' field to True, indicating that local uploads are enabled.

    :param kwargs: A dictionary of keyword arguments (not used).
    :return: A dictionary containing the resolved payload with 'local_upload' set to True.
    """
    return {"local_upload": True}
