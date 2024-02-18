# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.ConfigCheck


class Box:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):

        # Early exit if we're creating this with a bulk route
        if (_Configuration == None):
            return

        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Box On Server
        QueryList:list = []
        QueryList.append({
                "BoxCreate": {
                "CenterPosX_um": _Configuration.CenterPosition_um[0],
                "CenterPosY_um": _Configuration.CenterPosition_um[1],
                "CenterPosZ_um": _Configuration.CenterPosition_um[2],
                "ScaleX_um": _Configuration.Dimensions_um[0],
                "ScaleY_um": _Configuration.Dimensions_um[1],
                "ScaleZ_um": _Configuration.Dimensions_um[2],
                "RotationX_rad": _Configuration.Rotation_rad[0],
                "RotationY_rad": _Configuration.Rotation_rad[1],
                "RotationZ_rad": _Configuration.Rotation_rad[2],
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        self.ID = Response["ShapeID"]



def BatchCreate(_Configs:list, _RequestHandler:object, _SimulationID:int):

    QueryList:list = []
    for _Configuration in _Configs:
        QueryList.append({
                "BoxCreate": {
                "CenterPosX_um": _Configuration.CenterPosition_um[0],
                "CenterPosY_um": _Configuration.CenterPosition_um[1],
                "CenterPosZ_um": _Configuration.CenterPosition_um[2],
                "ScaleX_um": _Configuration.Dimensions_um[0],
                "ScaleY_um": _Configuration.Dimensions_um[1],
                "ScaleZ_um": _Configuration.Dimensions_um[2],
                "RotationX_rad": _Configuration.Rotation_rad[0],
                "RotationY_rad": _Configuration.Rotation_rad[1],
                "RotationZ_rad": _Configuration.Rotation_rad[2],
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)

    Objects:list = []
    for i in range(len(Response)):
        Object = Box(None, None, None)
        Object.ID = Response[i]["ShapeID"]
        Object.Name = _Configs[i].Name
        Objects.append(Object)
    return Objects

