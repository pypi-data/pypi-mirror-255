from datetime import datetime
from .address import Address
from enum import Enum


class Title(Enum):
    """Title

    Values:
        EMPTY
        MR
        MRS
        MX
    """

    EMPTY = None
    MR = "mr"
    MRS = "mrs"
    MX = "mx"


class User:
    """User information
    to be sent inside the user object
    to the DataDome Fraud API

    Attributes:
        id: A unique customer identifier from your system.
        title: Title of the user
        firstname: First name of the user
        lastname: Last name of the user
        createdAt: Creation date of the user, Format ISO 8601 YYYY-MM-DDThh:mm:ssTZD
        email: Email of the user
        address: Address of the user
    """

    def __init__(
        self,
        id,
        title=Title.EMPTY,
        firstname=None,
        lastname=None,
        createdAt=datetime.now(),  # noqa: E501
        phone=None,
        email=None,
        address=Address(),
    ):
        self.id = id
        if hasattr(title, "value"):
            self.title = title.value
        self.firstname = firstname
        self.lastname = lastname
        self.createdAt = createdAt
        self.phone = phone
        self.email = email
        self.address = address

    def __str__(self):
        return (
            "User: id="
            + self.id
            + "\n title="
            + self.title
            + "\n firstname="
            + self.firstname
            + "\n lastname="
            + self.lastname
            + "\n createdAt="
            + self.createdAt
            + "\n phone="
            + self.phone
            + "\n email="
            + self.email
            + "\n address="
            + str(self.address)
        )


class UserSession:
    """Session information
    to be sent inside the session object
    to the DataDome Fraud API

    Attributes:
        id: A unique session identifier from your system
        createdAt: Creation date of the user, Format ISO 8601 YYYY-MM-DDThh:mm:ssTZD
    """

    def __init__(
        self,
        id=None,
        createdAt=datetime.now(),
    ):
        self.id = id
        self.createdAt = createdAt

    def __str__(self):
        return "UserSession: id=" + self.id + "\n createdAt=" + self.createdAt
