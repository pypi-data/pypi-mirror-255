# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.GetID
import BrainGenix.LibUtils.ConfigCheck

class BS:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):

        # Early exit if we're creating this with a bulk route
        if (_Configuration == None):
            return
    
        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create On Server
        ShapeID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Shape)
        QueryList:list = []
        QueryList.append({
            "BSCreate": {
                "ShapeID": ShapeID,
                "MembranePotential_mV": _Configuration.MembranePotential_mV,
                "SpikeThreshold_mV": _Configuration.SpikeThreshold_mV,
                "DecayTime_ms": _Configuration.DecayTime_ms,
                "RestingPotential_mV": _Configuration.RestingPotential_mV,
                "AfterHyperpolarizationAmplitude_mV": _Configuration.AfterHyperpolarizationAmplitude_mV,
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        self.ID = Response["CompartmentID"]



def BatchCreate(_Configs:list, _RequestHandler:object, _SimulationID:int):

    QueryList:list = []
    for _Configuration in _Configs:
        ShapeID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Shape)
        QueryList.append({
            "BSCreate": {
                "ShapeID": ShapeID,
                "MembranePotential_mV": _Configuration.MembranePotential_mV,
                "SpikeThreshold_mV": _Configuration.SpikeThreshold_mV,
                "DecayTime_ms": _Configuration.DecayTime_ms,
                "RestingPotential_mV": _Configuration.RestingPotential_mV,
                "AfterHyperpolarizationAmplitude_mV": _Configuration.AfterHyperpolarizationAmplitude_mV,
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)

    Objects:list = []
    for i in range(len(Response)):
        Object = BS(None, None, None)
        Object.ID = Response[i]["CompartmentID"]
        Object.Name = _Configs[i].Name
        Objects.append(Object)
    return Objects
