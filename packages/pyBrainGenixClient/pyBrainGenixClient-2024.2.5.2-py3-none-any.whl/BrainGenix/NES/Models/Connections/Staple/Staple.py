# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.GetID
import BrainGenix.LibUtils.ConfigCheck


class Staple:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.Name =  _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Box On Server
        SourceCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.SourceCompartment)
        DestinationCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.DestinationCompartment)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Connection/Staple/Create?SimulationID={_SimulationID}&Name={_Configuration.Name}&SourceCompartmentID={SourceCompartmentID}&DestinationCompartmentID={DestinationCompartmentID}")
        assert(Response != None)
        self.ID = Response["StapleID"]