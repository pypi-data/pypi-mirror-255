# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.ConfigCheck

class Sphere:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):

        # Early exit if we're creating this with a bulk route
        if (_Configuration == None):
            return

        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Sphere On Server
        QueryList:list = []
        QueryList.append({
                "SphereCreate": {
                "Radius_um": _Configuration.Radius_um,
                "CenterPosX_um": _Configuration.Center_um[0],
                "CenterPosY_um": _Configuration.Center_um[1],
                "CenterPosZ_um": _Configuration.Center_um[2],
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
                "SphereCreate": {
                "Radius_um": _Configuration.Radius_um,
                "CenterPosX_um": _Configuration.Center_um[0],
                "CenterPosY_um": _Configuration.Center_um[1],
                "CenterPosZ_um": _Configuration.Center_um[2],
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)



    Objects:list = []
    for i in range(len(Response)):
        Object = Sphere(None, None, None)
        Object.ID = Response[i]["ShapeID"]
        Object.Name = _Configs[i].Name
        Objects.append(Object)
    return Objects