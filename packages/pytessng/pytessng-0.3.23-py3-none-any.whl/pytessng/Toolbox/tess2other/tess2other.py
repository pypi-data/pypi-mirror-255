from .tess2opendrive import tess2opendrive
from .tess2shape import tess2shape
from .tess2unity import tess2unity
from .tess2json import tess2json


def tess2other(netiface, params, mode):
    if mode == "opendrive":
        tess2opendrive.tess2opendrive(netiface, params)
    elif mode == "shape":
        tess2shape.tess2shape(netiface, params, mode="shape")
    elif mode == "geojson":
        tess2shape.tess2shape(netiface, params, mode="geojson")
    elif mode == "unity":
        tess2unity.tess2unity(netiface, params)
    elif mode == "json":
        tess2json.tess2json(netiface, params)
    else:
        raise Exception("No this export mode!")
