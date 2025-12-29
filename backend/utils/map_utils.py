# utils/map_utils.py
# Utility functions to convert between a 0-99 grid and lat/lon using a bounding box.
# The bbox should be a dict: {'lat_min':..., 'lat_max':..., 'lon_min':..., 'lon_max':...}

from typing import Tuple


def clamp(val, a, b):
    return max(a, min(b, val))


def grid_to_latlon(x: int, y: int, bbox: dict) -> Tuple[float, float]:
    """Convert grid coordinates (0..99) to (lat, lon) within bbox.

    We map x -> lon (lon_min..lon_max) and y -> lat (lat_max..lat_min) so that
    y=0 corresponds to lat_max (top) and y=99 to lat_min (bottom).
    """
    if bbox is None:
        raise ValueError("bbox must be provided")

    x = clamp(int(x), 0, 99)
    y = clamp(int(y), 0, 99)

    lon_min = float(bbox.get('lon_min'))
    lon_max = float(bbox.get('lon_max'))
    lat_min = float(bbox.get('lat_min'))
    lat_max = float(bbox.get('lat_max'))

    # fraction along x and y
    fx = x / 99.0
    fy = y / 99.0

    lon = lon_min + fx * (lon_max - lon_min)
    # invert y so that 0 -> lat_max
    lat = lat_max - fy * (lat_max - lat_min)

    return (lat, lon)


def latlon_to_grid(lat: float, lon: float, bbox: dict) -> Tuple[int, int]:
    """Convert lat/lon inside bbox to grid coordinates (0..99).

    Returns integers clamped to 0..99.
    """
    if bbox is None:
        raise ValueError("bbox must be provided")

    lon_min = float(bbox.get('lon_min'))
    lon_max = float(bbox.get('lon_max'))
    lat_min = float(bbox.get('lat_min'))
    lat_max = float(bbox.get('lat_max'))

    if lon_max == lon_min or lat_max == lat_min:
        raise ValueError("Invalid bbox ranges")

    fx = (float(lon) - lon_min) / (lon_max - lon_min)
    fy = (lat_max - float(lat)) / (lat_max - lat_min)

    x = int(round(fx * 99))
    y = int(round(fy * 99))

    x = clamp(x, 0, 99)
    y = clamp(y, 0, 99)

    return (x, y)

