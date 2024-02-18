# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.ConfigCheck


class Cylinder:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):

        # Early exit if we're creating this with a bulk route
        if (_Configuration == None):
            return
        
        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Cylinder On Server
        QueryList:list = []
        QueryList.append({
                "CylinderCreate": {
                "Point1Radius_um": _Configuration.Point1Radius_um,
                "Point1PosX_um": _Configuration.Point1Position_um[0],
                "Point1PosY_um": _Configuration.Point1Position_um[1],
                "Point1PosZ_um": _Configuration.Point1Position_um[2],
                "Point2Radius_um": _Configuration.Point2Radius_um,
                "Point2PosX_um": _Configuration.Point2Position_um[0],
                "Point2PosY_um": _Configuration.Point2Position_um[1],
                "Point2PosZ_um": _Configuration.Point2Position_um[2],
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
                "CylinderCreate": {
                "Point1Radius_um": _Configuration.Point1Radius_um,
                "Point1PosX_um": _Configuration.Point1Position_um[0],
                "Point1PosY_um": _Configuration.Point1Position_um[1],
                "Point1PosZ_um": _Configuration.Point1Position_um[2],
                "Point2Radius_um": _Configuration.Point2Radius_um,
                "Point2PosX_um": _Configuration.Point2Position_um[0],
                "Point2PosY_um": _Configuration.Point2Position_um[1],
                "Point2PosZ_um": _Configuration.Point2Position_um[2],
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)

    Objects:list = []
    for i in range(len(Response)):
        Object = Cylinder(None, None, None)
        Object.ID = Response[i]["ShapeID"]
        Object.Name = _Configs[i].Name
        Objects.append(Object)
    return Objects

