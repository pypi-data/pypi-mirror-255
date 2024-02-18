import time

try:
    from importlib import metadata
except ImportError: # for Python<3.8
    import importlib_metadata as metadata

__version__ = metadata.version("datadome_fraud_sdk_python")


class DataDomeModule:
    """ Information from the SDK
    to be sent inside the module object
    to the DataDome Fraud API
    
    Attributes:
        requestTimeMicros: Timestamp of the request, in milliseconds
        name:  name of the SDK
        version: version of the SDK         
    """
    def __init__(self, version=__version__):
        self.requestTimeMicros = int(time.time() * 1000000)
        self.name = "Fraud SDK Python"
        self.version = version
