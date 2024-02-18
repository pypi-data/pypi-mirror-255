from enum import Enum
from .user import UserSession

class ActionType(Enum):
    """ Event action type
    
    Values:
        LOGIN
        REGISTER
    """
    LOGIN = "login"
    REGISTER = "registration"


class StatusType(Enum):
    """ Event status type
    
    Values:
        SUCCEEDED
        FAILED
    """
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNDEFINED = "undefined"


class DataDomeEvent:
    """ Event to be protected by the DataDome Fraud API
    
    Attributes:
        action: ActionType
        account: User account (mail address, username, alias, login, ...)
        status: StatusType
    """
    def __init__(self, action, account, status=StatusType.UNDEFINED):
        self.action = action
        self.account = account
        self.status = status

    def merge_with(self, request_data):
        request_data.event = self.action.value
        request_data.account = self.account
        request_data.status = self.status.value
        return request_data

    def __str__(self):
        return ("Event: action=" + self.action + "\n" 
                + "account=" + self.account + "\n"
                + "status=" + self.status)


class LoginEvent(DataDomeEvent):
    """ Login Event
    
    Attributes:
        action: ActionType.LOGIN
        account: User account (mail address, username, alias, login, ...)
        status: StatusType
    """
    def __init__(self, account, status=StatusType.UNDEFINED):
        super().__init__(ActionType.LOGIN, account, status)


class RegistrationEvent(DataDomeEvent):
    """ Registration Event
    
    Attributes:
        action: ActionType.REGISTRATION
        account: User account (mail address, username, alias, login, ...)
        status: StatusType
    """
    def __init__(self, account, user, 
                 session=UserSession(), status=StatusType.UNDEFINED):
        super().__init__(ActionType.REGISTER, account, status)
        self.session = session
        self.user = user

    def merge_with(self, request_data):
        request_data = super().merge_with(request_data)
        request_data.session = self.session
        request_data.user = self.user
        return request_data
