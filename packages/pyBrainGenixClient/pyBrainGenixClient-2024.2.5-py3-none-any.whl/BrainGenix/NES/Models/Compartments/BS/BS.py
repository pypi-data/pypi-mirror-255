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

        # Create Box On Server
        ShapeID = BrainGenix.LibUtils.GetID.GetID(_Configuration.Shape)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Compartment/BS/Create?SimulationID={_SimulationID}&Name={_Configuration.Name}&ShapeID={ShapeID}&MembranePotential_mV={_Configuration.MembranePotential_mV}&SpikeThreshold_mV={_Configuration.SpikeThreshold_mV}&DecayTime_ms={_Configuration.DecayTime_ms}&RestingPotential_mV={_Configuration.RestingPotential_mV}&AfterHyperpolarizationAmplitude_mV={_Configuration.AfterHyperpolarizationAmplitude_mV}")
        assert(Response != None)
        self.ID = Response["CompartmentID"]