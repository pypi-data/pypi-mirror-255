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
        CenterPos = json.dumps(_Configuration.Center_um)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Geometry/Shape/Sphere/Create?SimulationID={_SimulationID}&Name={_Configuration.Name}&Radius_um={_Configuration.Radius_um}&Center_um={CenterPos}")
        assert(Response != None)
        self.ID = Response["ShapeID"]