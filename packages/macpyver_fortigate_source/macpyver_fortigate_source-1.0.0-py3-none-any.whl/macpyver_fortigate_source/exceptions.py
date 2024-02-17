"""Module with exceptions for the FortiGate Source."""


class FortiGateSource(Exception):
    """Base class for all exceptions related to FortiGate Source."""


class FortiGateAPIError(FortiGateSource):
    """Exception when a API error occurs."""
