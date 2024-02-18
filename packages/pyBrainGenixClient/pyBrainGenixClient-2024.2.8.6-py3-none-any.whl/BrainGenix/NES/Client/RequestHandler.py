# BrainGenix-NES
# AGPLv3

import requests
import time
import requests_futures.sessions
import json

class RequestHandler:

    def __init__(self, _URIBase:str, _Token:str):
        self.URIBase = _URIBase
        self.Token = _Token
        self.RequestID:int = 0
        self.FuturesSession = requests_futures.sessions.FuturesSession()

        # Check that API is up
        try:
            Response = requests.get(f"{self.URIBase}/Hello")
        except:
            raise ConnectionError("Unable To Connect To API Endpoint")
        

    
    # Make Query
    def MakeQuery(self, _URIStub:str):
        
        # Exception Handling For Network Errors
        Response = None
        for RetryCount in range(8):
            try:
                Response = requests.get(f"{self.URIBase}{_URIStub}")
                break
            except Exception as E:
                time.sleep(1)
                if (RetryCount == 7):
                    raise ConnectionError("Error Communicating With API, An IncompleteRead Has Occured!")
                else:
                    print("\n---------------")
                    print(f"Warning, Attempt {RetryCount} Has Failed, Retrying Query {self.URIBase}{_URIStub}")
                    print(f"Python Reports Error: {E}")
                    print("---------------\n")

        # Parse the Response, Return It
        ResponseJSON = Response.json()
        if (ResponseJSON["StatusCode"] != 0):
            raise ConnectionError(f"Error During API Call To '{self.URIBase}{_URIStub}', API Returned Status Code '{ResponseJSON['StatusCode']}'")
            return None
        return ResponseJSON



    def MakeAuthenticatedQuery(self, _URIStub:str):
        URIStub = f"{_URIStub}&AuthKey={self.Token}"
        return self.MakeQuery(URIStub)
    


    def MakeAuthenticatedAsyncQueries(self, _URIList:list):

        # Enumerate URI Stubs And Add Base, AuthKey
        Futures:list = []
        for URI in _URIList:
            Futures.append(self.FuturesSession.get(f"{self.URIBase}{URI}&AuthKey={self.Token}"))
        
        # Get Responses
        ResponsesJSON:list = []
        for Future in Futures:
            ResponsesJSON.append(Future.result().json())

        return ResponsesJSON
    
    def BuildPostQuery(self, _IndividualQueries:list, _URIStub:str="/NES")->str:

        RequestData:list = []
        RequestUUIDs:list = []

        for Query in _IndividualQueries:
            ThisUUID = self.RequestID
            self.RequestID += 1
            Query["ReqID"] = ThisUUID
            RequestUUIDs.append(ThisUUID)
            RequestData.append(Query)

        ResponseJSONStr = self.MakePostQuery(RequestData, _URIStub)

        return ResponseJSONStr

    def MakePostQuery(self, _JSONData:dict, _URIStub:str="/NES"):

        # Exception Handling For Network Errors
        Response = None
        for RetryCount in range(8):
            try:
                Response = requests.post(f"{self.URIBase}{_URIStub}?AuthKey={self.Token}", json=_JSONData)
                break
            except Exception as E:
                time.sleep(1)
                if (RetryCount == 7):
                    raise ConnectionError("Error Communicating With API, An IncompleteRead Has Occured!")
                else:
                    print("\n---------------")
                    print(f"Warning, Attempt {RetryCount} Has Failed, Retrying Query {self.URIBase}{_URIStub}")
                    print(f"Python Reports Error: {E}")
                    print("---------------\n")

        # Parse the Response, Return It
        ResponseJSON = Response.json()
        return ResponseJSON


