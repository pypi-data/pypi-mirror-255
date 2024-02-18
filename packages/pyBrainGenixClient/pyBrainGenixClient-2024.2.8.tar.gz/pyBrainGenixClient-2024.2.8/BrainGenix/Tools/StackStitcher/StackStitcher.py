# BrainGenix-NES
# AGPLv3

import os
import sys
import imageio

import PIL.Image
import PIL.ImageDraw


class SliceStitcher:
    def __init__(
        self,
        _Verbose: bool = False,
        _AddBorders: bool = False,
        _BorderSize_px: int = 8,
        _LabelImages: bool = False,
        _MakeGif: bool = False,
    ):
        self.Verbose = _Verbose
        self.AddBorders = _AddBorders
        self.LabelImages = _LabelImages
        self.BorderSize_px = _BorderSize_px
        self.MakeGif = _MakeGif

    def GetNumberOfSlices(self, _FileList: list, _SimulationID: int, _RegionID: int):
        NumSlices: int = 0
        for File in _FileList:
            ParsedLine = File.replace(
                f"Simulation{_SimulationID}_Region{_RegionID}_Slice", ""
            )
            try:
                SliceNumber = int(ParsedLine.split("_")[0])
            except ValueError as e:
                print(f"Error parsing SliceNumber from {File}")
                continue

            NumSlices = max(SliceNumber, NumSlices)

        # slice numbers start at 0, so we're adding +1 due to that
        return NumSlices + 1

    def GetSimulationIDs(self, _FileList: list):
        SimulationIDs: list = []
        for File in _FileList:
            ParsedLine = File.replace("Simulation", "")
            SimulationID = int(ParsedLine.split("_")[0])

            if not SimulationID in SimulationIDs:
                SimulationIDs.append(SimulationID)

        return SimulationIDs

    def GetRegionIDs(self, _FileList: list, _SimulationID: int) -> list[int]:
        RegionIDs: list = []
        for File in _FileList:
            ParsedLine = File.replace(f"Simulation{_SimulationID}_Region", "")

            try:
                RegionID = int(ParsedLine.split("_")[0])
            except ValueError as e:
                print(f"Error parsing RegionID from {File}")
                continue
            if not RegionID in RegionIDs:
                RegionIDs.append(RegionID)

        return RegionIDs

    def StitchSlice(
        self,
        _DirectoryPath: str,
        _OutputDir: str,
        _FileNames: list,
        _SimulationID: int,
        _RegionID: int,
    ):
        # Sort filenames to only include those with this sim and region
        SortedFiles = []
        for File in _FileNames:
            if f"Simulation{_SimulationID}_Region{_RegionID}" not in File:
                continue
            SortedFiles.append(File)

        NumSlices = self.GetNumberOfSlices(_FileNames, _SimulationID, _RegionID)
        if self.Verbose:
            print(
                f"    - Simulation {_SimulationID} Region {_RegionID} Has {NumSlices} Slice(s)"
            )

        if not os.path.exists(_OutputDir):
            os.mkdir(_OutputDir)

        ReferenceImageSize = PIL.Image.open(_DirectoryPath + SortedFiles[0]).size

        # Lists to hold X and Y values
        Xvalues = []
        Yvalues = []
        for file_name in SortedFiles:
            File_NamexValue = file_name.find("_X")
            File_NameyValue = file_name.find("_Y")
            Xvalues.append(
                float("".join(file_name[File_NamexValue + i] for i in range(2, 8)))
            )
            Yvalues.append(
                float("".join(file_name[File_NameyValue + i] for i in range(2, 8)))
            )

        # Pair up the Xvalues and Y values into a list
        Yvalues = sorted(Yvalues)
        Xvalues = sorted(Xvalues)
        XList_Without_Duplicates = [val for val in set(Xvalues)]
        YList_Without_Duplicates = [val for val in set(Yvalues)]

        try:
            XIncrements = XList_Without_Duplicates[1] - XList_Without_Duplicates[0]
        except IndexError as e:
            print(
                f"Only found a single value within XList_Without_Duplicates: cannot calculate XIncrements"
            )
            raise e
        try:
            YIncrements = YList_Without_Duplicates[1] - YList_Without_Duplicates[0]
        except IndexError as e:
            print(
                f"Only found a single value within YList_Without_Duplicates: cannot calculate YIncrements"
            )
            raise e

        XTileCounter = len(XList_Without_Duplicates)
        YTileCounter = len(YList_Without_Duplicates)

        # Keep Track Of List Of Slice Images For Gif (If Enabled)
        SliceFilenames: list = []

        OutputImageSize = [
            ReferenceImageSize[0] * XTileCounter,
            ReferenceImageSize[1] * YTileCounter,
        ]
        if self.AddBorders:
            OutputImageSize[0] += self.BorderSize_px * (XTileCounter + 1)
            OutputImageSize[1] += self.BorderSize_px * (YTileCounter + 1)

        for ThisSliceNumber in range(NumSlices):
            OutputSliceImage = PIL.Image.new("RGBA", OutputImageSize, (0, 255, 0, 255))

            for x in range(XTileCounter):
                for y in range(YTileCounter):
                    xposition = round(x * XIncrements, 2)
                    yposition = round(y * YIncrements, 2)

                    HasFoundImage = False
                    for XRoundingError in range(-5, 5):
                        for YRoundingError in range(-5, 5):
                            XPositionWithRoundingError = xposition + (
                                XRoundingError * 0.01
                            )
                            YPositionWithRoundingError = yposition + (
                                YRoundingError * 0.01
                            )

                            xpositionstring = f"{XPositionWithRoundingError:.6f}"
                            ypositionstring = f"{YPositionWithRoundingError:.6f}"

                            try:
                                TileImage = PIL.Image.open(
                                    _DirectoryPath
                                    + f"Simulation{_SimulationID}_Region{_RegionID}_Slice{ThisSliceNumber}_X"
                                    + xpositionstring
                                    + "_Y"
                                    + ypositionstring
                                    + ".png"
                                )

                                # Optionally Label The Images Based On Position
                                if self.LabelImages:
                                    Overlay = PIL.ImageDraw.Draw(TileImage)
                                    Overlay.text(
                                        (16, 16),
                                        f"X{xpositionstring}um, Y{ypositionstring}um, Slice {ThisSliceNumber}",
                                        fill=(255, 0, 0),
                                    )

                                position = [
                                    x * ReferenceImageSize[0],
                                    y * ReferenceImageSize[1],
                                ]  # Corrected positions

                                if self.AddBorders:
                                    position[0] += (x + 1) * self.BorderSize_px
                                    position[1] += (y + 1) * self.BorderSize_px

                                OutputSliceImage.paste(TileImage, position)
                                HasFoundImage = True
                                break

                            except FileNotFoundError:
                                # print(f"Failed To Find Image: 'Simulation{_SimulationID}_Region{_RegionID}_Slice{ThisSliceNumber}_X" + xpositionstring + "_Y" + ypositionstring + ".png'")
                                pass

                        if HasFoundImage:
                            break

                    if not HasFoundImage:
                        if self.Verbose:
                            print(
                                f"Error, could not find image for position {xposition}x, {yposition}y"
                            )

            # get slice number as a variable then use f string and i = i+1
            OutputImageFilename = f"{_OutputDir}/Simulation{_SimulationID}_Region{_RegionID}_Slice{ThisSliceNumber}.png"
            OutputSliceImage.save(OutputImageFilename)
            if self.MakeGif:
                SliceFilenames.append(OutputImageFilename)

            if self.Verbose:
                print(
                    f"     - Stitched Simulation {_SimulationID} Region {_RegionID} Slice {ThisSliceNumber} ({XTileCounter}x{YTileCounter} images)"
                )

        # Now, Create The Gif
        if self.MakeGif:
            self.CreateGif(_SimulationID, _RegionID, _OutputDir, SliceFilenames)

    def CreateGif(
        self,
        _SimulationID: int,
        _RegionID: int,
        _OutputDir: str,
        _SliceFilenames: list[str],
    ):
        if self.Verbose:
            print(
                f"    - Creating Gif For Simulation {_SimulationID} Region {_RegionID}, This May Take A While"
            )

        GifFilename: str = (
            f"{_OutputDir}/Simulation{_SimulationID}_Region{_RegionID}.gif"
        )
        with imageio.get_writer(GifFilename, mode="I", loop=0) as Writer:
            for Filename in _SliceFilenames:
                Image = imageio.v3.imread(Filename)
                ImageNoAlpha = Image[:, :, :3]
                Writer.append_data(ImageNoAlpha)

        if self.Verbose:
            print(
                f"    - Created Gif For Simulation {_SimulationID} Region {_RegionID}"
            )


def StackStitcher(
    _InputDirectory: str,
    _OutputDirectory: str = "OutDir",
    _AddBorders: bool = True,
    _LabelImages: bool = True,
    _BorderSize_px: int = 8,
    _MakeGif: bool = True,
    _Verbose=True,
):
    # Ensure Paths Ends With /
    if not _InputDirectory.endswith("/"):
        _InputDirectory += "/"

    # Setup Slice Stitcher
    SS: SliceStitcher = SliceStitcher(
        _Verbose, _AddBorders, _BorderSize_px, _LabelImages, _MakeGif
    )

    # Reconstruct
    Images = os.listdir(_InputDirectory)
    SimulationIDs = SS.GetSimulationIDs(Images)
    if _Verbose:
        print(f"Detected {len(SimulationIDs)} Simulation(s) To Stitch")
    for SimID in SimulationIDs:
        if _Verbose:
            print(f" - Stitching Simulation With ID {SimID}")

        Regions = SS.GetRegionIDs(Images, SimID)
        if _Verbose:
            print(f" - Detected {len(Regions)} Region(s) In Simulation")

        for RegionID in Regions:
            if _Verbose:
                print(f"  - Stitching Region {RegionID}")
            SS.StitchSlice(_InputDirectory, _OutputDirectory, Images, SimID, RegionID)
