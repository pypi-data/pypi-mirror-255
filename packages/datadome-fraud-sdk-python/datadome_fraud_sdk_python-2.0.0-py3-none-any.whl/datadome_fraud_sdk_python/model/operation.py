from enum import Enum


class OperationType(Enum):
    """ Fraud Protection operation type
    
    Values:
        VALIDATE
        COLLECT
    """
    VALIDATE = "validate"
    COLLECT = "collect"
