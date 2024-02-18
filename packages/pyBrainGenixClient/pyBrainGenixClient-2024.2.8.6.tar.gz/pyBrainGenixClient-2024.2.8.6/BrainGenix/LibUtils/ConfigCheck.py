# BrainGenix-NES
# AGPLv3

import inspect


def ConfigCheck(_ConfigurationObject:object):

    # Firstly, we're going to get a list of all attributes of this object
    AttributeList = dir(_ConfigurationObject)

    # Now, we enumerate these attribs, filter out those builtin to python (starting with __)
    for AttributeName in AttributeList:

        # If it starts with an underscore, skip it
        if (AttributeName.startswith("__")):
            continue

        # Now, check the value of this attribute
        ThisAttribute = getattr(_ConfigurationObject, AttributeName)

        # Check the values of these based on type, it should *never* be empty (we want users to fill out the config objects fully)
        if (ThisAttribute == ""):
            PrintErrorMessage(_ConfigurationObject, AttributeName)
        elif (ThisAttribute == None):
            PrintErrorMessage(_ConfigurationObject, AttributeName)



def PrintErrorMessage(_ConfigurationObject:object, _AttributeName:str):
    
    # Get Information From Class To Build Error Message
    ClassFileName:str = inspect.getfile(_ConfigurationObject.__class__).split("BrainGenix/")[1].strip(".py").replace("/", ".")
    ErrorMessage:str = f'''

    -----------------------
    Configuration Error In '{ClassFileName}', Attribute '{_AttributeName}' Was Left Uninitialized.
    Please Reference The API Spec For Usage Information.
    https://gitlab.braingenix.org/carboncopies/BrainGenix-API/-/blob/master/Docs/API.md?ref_type=heads
    If You Feel That This Is A Bug, Please Open An Issue Here:
    https://gitlab.braingenix.org/carboncopies/BrainGenix/NES/PythonClient/-/issues
    -----------------------
    '''

    # Now, Chuck An Error To stderr Alerting The User That There Is A Config Issue
    raise AttributeError(ErrorMessage)