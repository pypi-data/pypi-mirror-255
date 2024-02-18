"""MicroBees exceptions."""

class MicroBeesException(Exception):
    """Base exception class for MicroBees."""

class MicroBeesNotSupportedException(MicroBeesException):
    """Exception to indicate a requested action is not supported by MicroBees."""

class MicroBeesCredentialsException(MicroBeesException):
    """Exception to indicate something with credentials"""

class MicroBeesNoCredentialsException(MicroBeesCredentialsException):
    """Exception to indicate missing credentials"""

class MicroBeesWrongCredentialsException(MicroBeesCredentialsException):
    """Exception to indicate wrong credentials"""