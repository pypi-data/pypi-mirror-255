# BrainGenix-NES
# AGPLv3


def GetID(_Object):

    ID = None
    if (type(_Object) == str):
        ID = int(_Object)
    elif (type(_Object) == int):
        ID = int(_Object)
    else:
        ID = int(_Object.ID)

    return ID