# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.GetID
import BrainGenix.LibUtils.ConfigCheck


class PatchClampDAC:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.Name =  _Configuration.Name
        self.RequestHandler = _RequestHandler
        self.SimulationID = _SimulationID

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create On Server
        DestinationCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.DestinationCompartment)
        QueryList:list = []
        QueryList.append({
            "PatchClampDACCreate": {
                "DestinationCompartmentID": DestinationCompartmentID,
                "ClampPosX_um": _Configuration.ClampLocation_um[0],
                "ClampPosY_um": _Configuration.ClampLocation_um[1],
                "ClampPosZ_um": _Configuration.ClampLocation_um[2],
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        self.ID = Response["PatchClampDACID"]



    ## Access Methods
    def SetOutputList(self, _ControlData:list):
        QueryList:list = []
        QueryList.append({
            "PatchClampDACSetOutputList": {
                "ControlData": _ControlData,
                "PatchClampDACID": self.ID,
                "SimulationID": self.SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        return Response["StatusCode"]
    


def BatchCreate(_Configs:list, _RequestHandler:object, _SimulationID:int):

    QueryList:list = []
    for _Configuration in _Configs:
        DestinationCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.DestinationCompartment)
        QueryList.append({
            "PatchClampDACCreate": {
                "DestinationCompartmentID": DestinationCompartmentID,
                "ClampPosX_um": _Configuration.ClampLocation_um[0],
                "ClampPosY_um": _Configuration.ClampLocation_um[1],
                "ClampPosZ_um": _Configuration.ClampLocation_um[2],
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)

    Objects:list = []
    for i in range(len(Response)):
        Object = PatchClampDAC(None, None, None)
        Object.ID = Response[i]["StapleID"]
        Object.Name = _Configs[i].Name
        Objects.append(Object)
    return Objects
