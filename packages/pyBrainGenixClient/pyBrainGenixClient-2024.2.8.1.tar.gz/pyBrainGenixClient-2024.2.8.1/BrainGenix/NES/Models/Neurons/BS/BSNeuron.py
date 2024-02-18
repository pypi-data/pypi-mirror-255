# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.GetID
import BrainGenix.LibUtils.ConfigCheck


class BSNeuron:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create BSNeuron On Server
        self.SomaID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Soma)
        self.AxonID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Axon)
        QueryList:list = []
        QueryList.append({
            "BSNeuronCreate": {
                "AxonID": self.AxonID,
                "SomaID": self.SomaID,
                "MembranePotential_mV": _Configuration.MembranePotential_mV,
                "RestingPotential_mV": _Configuration.RestingPotential_mV,
                "SpikeThreshold_mV": _Configuration.SpikeThreshold_mV,
                "DecayTime_ms": _Configuration.DecayTime_ms,
                "AfterHyperpolarizationAmplitude_mV": _Configuration.AfterHyperpolarizationAmplitude_mV,
                "PostsynapticPotentialRiseTime_ms": _Configuration.PostsynapticPotentialRiseTime_ms,
                "PostsynapticPotentialDecayTime_ms": _Configuration.PostsynapticPotentialDecayTime_ms,
                "PostsynapticPotentialAmplitude_nA": _Configuration.PostsynapticPotentialAmplitude_nA,
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        self.ID = Response["NeuronID"]

def BatchCreate(_Configs:list, _RequestHandler:object, _SimulationID:int):

    QueryList:list = []
    for _Configuration in _Configs:
        SomaID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Soma)
        AxonID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Axon)
        QueryList.append({
            "BSNeuronCreate": {
                "AxonID": AxonID,
                "SomaID": SomaID,
                "MembranePotential_mV": _Configuration.MembranePotential_mV,
                "RestingPotential_mV": _Configuration.RestingPotential_mV,
                "SpikeThreshold_mV": _Configuration.SpikeThreshold_mV,
                "DecayTime_ms": _Configuration.DecayTime_ms,
                "AfterHyperpolarizationAmplitude_mV": _Configuration.AfterHyperpolarizationAmplitude_mV,
                "PostsynapticPotentialRiseTime_ms": _Configuration.PostsynapticPotentialRiseTime_ms,
                "PostsynapticPotentialDecayTime_ms": _Configuration.PostsynapticPotentialDecayTime_ms,
                "PostsynapticPotentialAmplitude_nA": _Configuration.PostsynapticPotentialAmplitude_nA,
                "Name": _Configuration.Name,
                "SimulationID": _SimulationID
            }
        })
    Response = _RequestHandler.BuildPostQuery(QueryList, "/NES")
    assert(Response != None)

    Objects:list = []
    for i in range(len(Response)):
        Object = BSNeuron(None, None, None)
        Object.ID = Response[i]["NeuronID"]
        Object.Name = _Configs[i].Name
        Object.SomaID = BrainGenix.LibUtils.GetID.GetID(_Configs[i].Soma)
        Object.AxonID = BrainGenix.LibUtils.GetID.GetID(_Configs[i].Axon)
        Objects.append(Object)
    return Objects

