from utils.is_num import is_num


def is_latitude_longitude(x):
    """"
    latitude coordinate is between -90 and 90.
    longitude coordinate is between -180 and 180.
    """
    if not isinstance(x, dict):
        return False

    if 'lat' not in x or 'lng' not in x:
        return False

    if not is_num(x['lat']) or not is_num(x['lng']):
        return False

    return -90 <= x['lat'] <= 90 and -180 <= x['lng'] <= 180


