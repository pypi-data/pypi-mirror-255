# BrainGenix-NES
# AGPLv3

import json
import os
import time
import math
import base64
import yaspin

from . import Configuration

from BrainGenix.NES.Client import RequestHandler
import BrainGenix.LibUtils.GetID

import BrainGenix.LibUtils.ConfigCheck


class Visualizer:

    def __init__(self, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.RequestHandler = _RequestHandler
        self.SimulationID = _SimulationID


    ## Access Methods
    def GenerateVisualization(self, _Configuration:object):

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        LocationList:list = []
        for i in range(len(_Configuration.CameraPositionList_um)):
            LocationList.append({
                "CameraPositionX_um": _Configuration.CameraPositionList_um[i][0],
                "CameraPositionY_um": _Configuration.CameraPositionList_um[i][1],
                "CameraPositionZ_um": _Configuration.CameraPositionList_um[i][2],
                "CameraLookAtPositionX_um": _Configuration.CameraLookAtPositionList_um[i][0],
                "CameraLookAtPositionY_um": _Configuration.CameraLookAtPositionList_um[i][1],
                "CameraLookAtPositionZ_um": _Configuration.CameraLookAtPositionList_um[i][2],
                "CameraFOV_deg": _Configuration.CameraFOVList_deg[i],
            })

        QueryList:list = []
        QueryList.append({
            "VisualizerGenerateImage": {
                "ImageWidth_px": _Configuration.ImageWidth_px,
                "ImageHeight_px": _Configuration.ImageHeight_px,
                "Locations": LocationList,
                "SimulationID": self.SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        return Response["StatusCode"]



    def GetStatus(self):

        QueryList:list = []
        QueryList.append({
            "VisualizerGetStatus": {
                "SimulationID": self.SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        return Response["VisualizerStatus"]



    def GetImageHandles(self):

        QueryList:list = []
        QueryList.append({
            "VisualizerGetImageHandles": {
                "SimulationID": self.SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        return json.loads(Response["ImageHandles"])



    def GetImages(self, _ImageHandles:list):
    
        QueryList:list = []

        for ImageHandle in _ImageHandles:
            QueryList.append({
                "VisualizerGetImage": {
                    "SimulationID": self.SimulationID,
                    "ImageHandle": ImageHandle
                }
            })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")
        assert(Response != None)
        
        ImageBytes:list = []
        for ImageResponse in Response:
            ImageBytes.append(bytes(ImageResponse["ImageData"], 'utf-8'))
        return ImageBytes


        
    def WaitUntilDone(self):

        WaitSpinner = yaspin.yaspin(text="Render Operation In Progress", color="green", timer=True)
        WaitSpinner.start()
        while (self.GetStatus() != 3):
            time.sleep(0.25)
        WaitSpinner.ok()



    def GetImageList(self):
        if self.GetStatus() != 3:
            raise Exception("Cannot get images, server is not done rendering yet!")
        return self.GetImageHandles()


    def SaveImages(self, _Prefix:str = "", _BatchSize:int = 10):

        # Check That The DirectoryPath Exists
        if not _Prefix.endswith("/"):
            _Prefix += "/"
        
        if not os.path.exists(_Prefix):
            os.makedirs(_Prefix)


        self.WaitUntilDone()


        WaitSpinner = yaspin.yaspin(text="Downlaoding Images", color="green", timer=True)
        WaitSpinner.start()

        ImageHandles:list = self.GetImageList()

        Total:int = 0
        for x in range(math.ceil(len(ImageHandles) / _BatchSize)):

            BatchHandles:list = []
            for i in range(_BatchSize):
                if (Total < len(ImageHandles)):
                    BatchHandles.append(ImageHandles[Total])
                    Total += 1


            ImageData:list = self.GetImages(BatchHandles)

            for i in range(len(BatchHandles)):

                with open(_Prefix + BatchHandles[i].split("/")[2], "wb") as FileHandler:
                    FileHandler.write(base64.decodebytes(ImageData[i]))

        WaitSpinner.ok()
