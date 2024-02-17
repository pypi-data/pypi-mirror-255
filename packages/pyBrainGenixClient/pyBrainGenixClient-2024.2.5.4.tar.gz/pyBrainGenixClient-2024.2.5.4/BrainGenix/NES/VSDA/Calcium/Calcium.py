# BrainGenix-NES
# AGPLv3

import json
import base64
import tqdm
import yaspin
import os
import time

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.ConfigCheck
import BrainGenix.LibUtils.GetID



class Calcium:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.RequestHandler = _RequestHandler
        self.SimulationID = _SimulationID

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create On Server
        NeuronTags:list = json.dumps(_Configuration.FlourescingNeuronTags)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/VSDA/Calcium/Setup?SimulationID={_SimulationID}&PixelResolution_nm={_Configuration.PixelResolution_nm}&ImageWidth_px={_Configuration.ImageWidth_px}&ImageHeight_px={_Configuration.ImageHeight_px}&SliceThickness_nm={_Configuration.SliceThickness_nm}&ScanRegionOverlap_percent={_Configuration.ScanRegionOverlap_percent}&MicroscopeFOV_deg={_Configuration.MicroscopeFOV_deg}&NumPixelsPerVoxel_px={_Configuration.NumPixelsPerVoxel_px}&FlourescingNeuronTags={NeuronTags}&ImagingInterval_ms={_Configuration.ImagingInterval_ms}")
        assert(Response != None)



    ## Access Methods
    def DefineScanRegion(self, _Point1_um:list, _Point2_um:list, _CalciumIndicator:object):
        Point1 = json.dumps(_Point1_um)
        Point2 = json.dumps(_Point2_um)
        CalciumID = BrainGenix.LibUtils.GetID.GetID(_CalciumIndicator)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/VSDA/Calcium/DefineScanRegion?SimulationID={self.SimulationID}&Point1_um={Point1}&Point2_um={Point2}&CalciumIndicatorID={CalciumID}")
        assert(Response != None)
        self.CalciumScanRegionID = Response["CalciumScanRegionID"]


    def QueueRenderOperation(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/VSDA/Calcium/QueueRenderOperation?SimulationID={self.SimulationID}&CalciumScanRegionID={self.CalciumScanRegionID}")
        assert(Response != None)
        return Response["StatusCode"]


    def GetRenderStatus(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/VSDA/Calcium/GetRenderStatus?SimulationID={self.SimulationID}")
        assert(Response != None)
        return Response
    

    def GetImageStack(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/VSDA/Calcium/GetImageStack?SimulationID={self.SimulationID}&CalciumScanRegionID={self.CalciumScanRegionID}")
        assert(Response != None)
        return Response["RenderedImages"]


    def GetImage(self, _ImageHandle:str):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/VSDA/Calcium/GetImage?SimulationID={self.SimulationID}&ImageHandle={_ImageHandle}")
        assert(Response != None)
        return bytes(Response["ImageData"], 'utf-8')
    

    def WaitForRender(self):

        # Setup Status Information
        StatusInfo:dict = self.GetRenderStatus()


        # Perform Sanity Check On Render
        if (StatusInfo["RenderStatus"] < 3):
            print("Error during rendering, API reports:\n")
            print(StatusInfo)


        # Block With Queued Spinner
        QueueSpinner = yaspin.yaspin(text="Render Operation In Queue, Elapsed Time", color="green", timer=True)
        QueueSpinner.start()
        while (StatusInfo["RenderStatus"] == 3):

            # Get Status Info, Wait To Avoid API Spam
            StatusInfo:dict = self.GetRenderStatus()
            time.sleep(0.25)

        QueueSpinner.ok()


        
        # Setup Slice, Image Status Bar
        SliceStatusBar = tqdm.tqdm("Rendering Slice", total=1)
        SliceStatusBar.leave = True
        SliceStatusBar.colour = "green"
        SliceStatusBar.bar_format = "{desc}{percentage:3.0f}%|{bar}| [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        LastSliceNumber = 0

        ImageStatusBar = tqdm.tqdm("Rendering Image", total=1)
        ImageStatusBar.leave = True
        ImageStatusBar.bar_format = "{desc}{percentage:3.0f}%|{bar}| [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        ImageStatusBar.colour = "magenta"


        # Block Execution Until Render Finishes, Update Bar As We Wait
        while (StatusInfo["RenderStatus"] != 5):

            # Update Slice Bar
            SliceStatusBar.total = int(StatusInfo["TotalSlices"])
            SliceStatusBar.n = max(int(StatusInfo["CurrentSlice"]), 0)
            SliceStatusBar.refresh()
            SliceStatusBar.set_description(f"Rendering Slice {str(StatusInfo['CurrentSlice']).rjust(5, '0')} / {str(StatusInfo['TotalSlices']).rjust(5, '0')}")


            # Update Image Bar
            if (SliceStatusBar.n > LastSliceNumber):
                LastSliceNumber = SliceStatusBar.n
                ImageStatusBar.reset()
            ImageStatusBar.total = int(StatusInfo["TotalSliceImages"])
            ImageStatusBar.n = max(int(StatusInfo["CurrentSliceImage"]), 0)
            ImageStatusBar.refresh()
            ImageStatusBar.set_description(f"Rendering Image {str(StatusInfo['CurrentSliceImage']).rjust(5, '0')} / {str(StatusInfo['TotalSliceImages']).rjust(5, '0')}")



            # Get Status Info, Wait To Avoid API Spam
            StatusInfo:dict = self.GetRenderStatus()
            time.sleep(0.1)
        
    
        # When we're done, rendering is finished - make it look like it truly is, then close the bar
        SliceStatusBar.total = int(StatusInfo["TotalSlices"])
        SliceStatusBar.n = int(StatusInfo["TotalSlices"])
        SliceStatusBar.set_description(f"Rendering Slice {str(StatusInfo['TotalSlices']).rjust(5, '0')} / {str(StatusInfo['TotalSlices']).rjust(5, '0')}")
        SliceStatusBar.refresh()
        SliceStatusBar.close()
        ImageStatusBar.total = int(StatusInfo["TotalSliceImages"])
        ImageStatusBar.n = int(StatusInfo["TotalSliceImages"])
        ImageStatusBar.set_description(f"Rendering Image {str(StatusInfo['TotalSliceImages']).rjust(5, '0')} / {str(StatusInfo['TotalSliceImages']).rjust(5, '0')}")
        ImageStatusBar.refresh()
        ImageStatusBar.close()


    def ThreadedSaveImageStack(self, _ImageStackDirectoryPrefix:str = "", _AsyncImages:int=10):

        # Check That The DirectoryPath Exists
        if not _ImageStackDirectoryPrefix.endswith("/"):
            _ImageStackDirectoryPrefix += "/"
        
        if not os.path.exists(_ImageStackDirectoryPrefix):
            os.makedirs(_ImageStackDirectoryPrefix)
            

        # Get Image Stack Manifest
        ImageHandles = self.GetImageStack()

        # Setup Progress Bar
        Bar = tqdm.tqdm("Downloading Image Stack", total=len(ImageHandles))
        Bar.leave = True
        Bar.bar_format = "{desc}{percentage:3.0f}%|{bar}| [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        Bar.colour = "green"


        for i in range(0, len(ImageHandles), _AsyncImages):

            # Make Batch Request URI List
            RequestURIs:list = []
            for x in range(i, i + _AsyncImages):
                RequestURIs.append(f"/NES/VSDA/EM/GetImage?SimulationID={self.SimulationID}&ImageHandle={ImageHandles[x]}")

            # Get Data
            Images = self.RequestHandler.MakeAuthenticatedAsyncQueries(RequestURIs)

            for Image in Images:
                ImageData = bytes(Image["ImageData"], 'utf-8')
                with open(_ImageStackDirectoryPrefix + ImageHandles[i].split("/")[1], "wb") as FileHandler:
                    FileHandler.write(base64.decodebytes(ImageData))

            Bar.set_description(f"Downloading Image {str(i + 1).rjust(5, '0')} / {str(len(ImageHandles)).rjust(5, '0')}")

            # Count Up Bar
            Bar.n = i + _AsyncImages
            Bar.refresh()

        
        # Finalize Bar
        Bar.set_description(f"Downloading Image {str(len(ImageHandles)).rjust(5, '0')} / {str(len(ImageHandles)).rjust(5, '0')}")
        Bar.n = len(ImageHandles)
        Bar.refresh()

        Bar.close()


    def SaveImageStack(self, _ImageStackDirectoryPrefix:str = ""):

        # Check That The DirectoryPath Exists
        if not _ImageStackDirectoryPrefix.endswith("/"):
            _ImageStackDirectoryPrefix += "/"
        
        if not os.path.exists(_ImageStackDirectoryPrefix):
            os.makedirs(_ImageStackDirectoryPrefix)
            

        # Get Image Stack Manifest
        ImageHandles = self.GetImageStack()

        # Setup Progress Bar
        Bar = tqdm.tqdm("Downloading Image Stack", total=len(ImageHandles))
        Bar.leave = True
        Bar.bar_format = "{desc}{percentage:3.0f}%|{bar}| [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        Bar.colour = "green"


        for i in range(len(ImageHandles)):

            # Save This Image
            ImageData = self.GetImage(ImageHandles[i])
            with open(_ImageStackDirectoryPrefix + ImageHandles[i].split("/")[1], "wb") as FileHandler:
                FileHandler.write(base64.decodebytes(ImageData))

            Bar.set_description(f"Downloading Image {str(i + 1).rjust(5, '0')} / {str(len(ImageHandles)).rjust(5, '0')}")

            # Count Up Bar
            Bar.n = i + 1
            Bar.refresh()

        Bar.close()
