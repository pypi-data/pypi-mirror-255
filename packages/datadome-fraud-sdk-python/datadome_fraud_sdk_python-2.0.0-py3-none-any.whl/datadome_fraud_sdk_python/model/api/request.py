from ..module import DataDomeModule
from ..headers import DataDomeMetadata
import json
import datetime


class DataDomeRequest:
    """DataDome Request object to be sent to the Fraud API

    Attributes:
        account: User account (mail address, username, alias, login, ...)
        header: Header sent by the User to the Customer endpoint
        module: Information about module sending this Payload
        status (for login protection): User login authentication status
        session (for registration protection): Information about the user session
        user (for registration protection): Information about the user session
    """

    def __init__(self, request):
        self.module = DataDomeModule()
        self.header = DataDomeMetadata(request)

    # we need to define `__iter__`, `__str__`, `__repr__`
    # and an encoder to make sure the json is properly created
    # from the object DataDomeRequest before being sent to the API
    def __iter__(self):
        yield from {
            "module": self.module,
            "header": self.header,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), cls=DdEncoder, ensure_ascii=False)

    def __repr__(self):
        return self.__str__()


class DdEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.astimezone().isoformat()
        return obj.__dict__
