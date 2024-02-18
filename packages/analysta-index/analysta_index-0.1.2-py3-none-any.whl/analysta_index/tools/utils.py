import json


def unpack_json(json_data):
    if (isinstance(json_data, str)):
        if '```json' in json_data:
            json_data = json_data.replace('```json', '').replace('```', '')
            return json.loads(json_data)
        return json.loads(json_data)
    elif (isinstance(json_data, dict)):
        return json_data
    else:
        raise ValueError("Wrong type of json_data")


def download_nltk(target, force=False):
    """ Download NLTK punkt """
    from . import state  # pylint: disable=C0415
    #
    if state.nltk_punkt_downloaded and not force:
        return
    #
    import ssl  # pylint: disable=C0415
    #
    try:
        _create_unverified_https_context = ssl._create_unverified_context  # pylint: disable=W0212
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context  # pylint: disable=W0212
    #
    import os  # pylint: disable=C0415
    import nltk  # pylint: disable=C0415,E0401
    import nltk.downloader  # pylint: disable=C0415,E0401
    #
    os.makedirs(target, exist_ok=True)
    #
    nltk.downloader._downloader._download_dir = target  # pylint: disable=W0212
    nltk.data.path = [target]
    #
    nltk.download("punkt", download_dir=target)
    #
    state.nltk_punkt_downloaded = True
