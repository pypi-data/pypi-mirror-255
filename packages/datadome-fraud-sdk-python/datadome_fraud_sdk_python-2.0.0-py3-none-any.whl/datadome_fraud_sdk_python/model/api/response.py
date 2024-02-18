from enum import Enum
from ..address import Address


class ResponseAction(Enum):
    ALLOW = "allow"
    DENY = "deny"


class ResponseStatus(Enum):
    OK = "ok"
    FAILURE = "failure"
    TIMEOUT = "timeout"

class DataDomeResponse:
    """ Response from DataDome Fraud API
    
    Attributes:
        action: Action answered to Customer endpoint
        reasons: Reasons of the action response
        ip: User IP
        location: User Location
    """
    def __init__(self, action = None, status = None, 
                 reasons = None, ip = None, location = None  ):
        self.action = action
        self.status = status
        self.reasons = reasons
        self.ip = ip
        self.location = location
        
    def update_with_api_response(self, api_response):
        self.status = ResponseStatus.OK
        if api_response.get("action", "") == "deny":
            self.action = ResponseAction.DENY
        else:
            self.action = ResponseAction.ALLOW
        self.reasons = api_response.get("reasons", "")
        self.ip = api_response.get("ip", "")
        location = api_response.get("location", None)
        if location is not None:
            countrycode = location.get("countryCode", "")
            country = location.get("country", "")
            city = location.get("city", "")
            self.location = Address(countrycode, country, city)
            
    def __str__(self):
        return ("DataDomeResponse: action:" + self.action.value
                + "\n status=" + self.status.value  
                + "\n reasons=" + str(self.reasons)
                + "\n ip=" + self.ip 
                + "\n location=" + str(self.location))
        

class DataDomeResponseError(DataDomeResponse):
    """ Response from DataDome Fraud API in case of an error
    
    Attributes:
        status: The status code of the response
        message: Description of the error
        errors: List of the fields in error
    """
    def __init__(self, api_response = {}, 
                 status = ResponseStatus.FAILURE, 
                 action = None):
        super().__init__(action=action)
        self.status = status
        self.message = api_response.get("message", "")
        self.errors = api_response.get("errors", "")

    def __str__(self):
        reasons = ""
        for i in self.errors:
            reasons += str(i) + ","
        return ("DataDomeResponseError: status=" + self.status.value 
                + "\n message=" + self.message 
                + "\n errors=" + reasons)