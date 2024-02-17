# BrainGenix-NES
# AGPLv3

import requests
import time
import requests_futures.sessions


class RequestHandler:

    def __init__(self, _URIBase:str, _Token:str):
        self.URIBase = _URIBase
        self.Token = _Token
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

    # Make a POST Query, as used for pure JSON requests
    def MakePOSTQuery(self, RequestJSONstr:str):
        url = f'http://localhost:8000/NES?AuthKey={self.Token}'

        # Exception Handling For Network Errors
        for RetryCount in range(8):
            try:
                Response = requests.post(url, json=RequestJSONstr)
                break
            except Exception as E:
                time.sleep(1)
                if (RetryCount == 7):
                    raise ConnectionError("Error Communicating With API, An IncompleteRead Has Occured!")
                else:
                    print("\n---------------")
                    print(f"Warning, Attempt {RetryCount} Has Failed, Retrying NES Query {RequestJSONstr}")
                    print(f"Python Reports Error: {E}")
                    print("---------------\n")
        

        return Response # let's just do this for the moment while we test this!

        # # Parse the Response, Return It
        # ResponseJSON = Response.json()
        # if (ResponseJSON["StatusCode"] != 0):
        #     raise ConnectionError(f"Error During NES API Call '{RequestJSONstr}', API Returned Status Code '{ResponseJSON['StatusCode']}'")
        #     return None
        # return ResponseJSON


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