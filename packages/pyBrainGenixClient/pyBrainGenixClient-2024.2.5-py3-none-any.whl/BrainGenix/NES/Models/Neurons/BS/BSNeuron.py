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
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Neuron/BSNeuron/Create"
            + f"?SimulationID={_SimulationID}"
            + f"&Name={_Configuration.Name}"
            + f"&SomaID={self.SomaID}"
            + f"&AxonID={self.AxonID}"
            + f"&MembranePotential_mV={_Configuration.MembranePotential_mV}"
            + f"&RestingPotential_mV={_Configuration.RestingPotential_mV}"
            + f"&SpikeThreshold_mV={_Configuration.SpikeThreshold_mV}"
            + f"&DecayTime_ms={_Configuration.DecayTime_ms}"
            + f"&AfterHyperpolarizationAmplitude_mV={_Configuration.AfterHyperpolarizationAmplitude_mV}"
            + f"&PostsynapticPotentialRiseTime_ms={_Configuration.PostsynapticPotentialRiseTime_ms}"
            + f"&PostsynapticPotentialDecayTime_ms={_Configuration.PostsynapticPotentialDecayTime_ms}"
            + f"&PostsynapticPotentialAmplitude_mV={_Configuration.PostsynapticPotentialAmplitude_mV}"
            )
        assert(Response != None)
        self.ID = Response["NeuronID"]
