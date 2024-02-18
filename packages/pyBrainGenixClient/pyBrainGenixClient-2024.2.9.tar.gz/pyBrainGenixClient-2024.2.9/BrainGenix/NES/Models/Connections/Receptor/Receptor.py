# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.GetID
import BrainGenix.LibUtils.ConfigCheck


class Receptor:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Box On Server
        SourceCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.SourceCompartment)
        DestinationCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.DestinationCompartment)
        ReceptorLocation = json.dumps(_Configuration.ReceptorLocation_um)
        QueryList:list = []
        QueryList.append({
            "ReceptorCreate": {
                "SourceCompartmentID": SourceCompartmentID,
                "DestinationCompartmentID": DestinationCompartmentID,
                "ReceptorPosX_um": _Configuration.ReceptorLocation_um[0],
                "ReceptorPosY_um": _Configuration.ReceptorLocation_um[1],
                "ReceptorPosZ_um": _Configuration.ReceptorLocation_um[2],
                "Conductance_nS": _Configuration.Conductance_nS,
                "TimeConstantRise_ms": _Configuration.TimeConstantRise_ms,
                "TimeConstantDecay_ms": _Configuration.TimeConstantDecay_ms,
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        self.ID = Response["ReceptorID"]


def BatchCreate(_Configs:list, _RequestHandler:object, _SimulationID:int):

    QueryList:list = []
    for _Configuration in _Configs:
        SourceCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.SourceCompartment)
        DestinationCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.DestinationCompartment)
        QueryList.append({
            "ReceptorCreate": {
                "SourceCompartmentID": SourceCompartmentID,
                "DestinationCompartmentID": DestinationCompartmentID,
                "ReceptorPosX_um": _Configuration.ReceptorLocation_um[0],
                "ReceptorPosY_um": _Configuration.ReceptorLocation_um[1],
                "ReceptorPosZ_um": _Configuration.ReceptorLocation_um[2],
                "Conductance_nS": _Configuration.Conductance_nS,
                "TimeConstantRise_ms": _Configuration.TimeConstantRise_ms,
                "TimeConstantDecay_ms": _Configuration.TimeConstantDecay_ms,
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)

    Objects:list = []
    for i in range(len(Response)):
        Object = Receptor(None, None, None)
        Object.ID = Response[i]["ReceptorID"]
        Object.Name = _Configs[i].Name
        Objects.append(Object)
    return Objects

