class PeliqanClientException(Exception):
    """
    Base exception raised by the Peliqan module.
    """


class OperationNotSupported(PeliqanClientException):
    """
        Raise this when an operation is not support by the client.
    """


class PeliqanJsonSerializerException(PeliqanClientException):
    """
        Raise this when an json encoding fails for a data structure.
    """
