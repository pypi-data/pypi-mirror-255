from gravybox.betterstack import collect_logger

logger = collect_logger()


class GravyboxException(Exception):
    pass


class UpstreamAPIFailure(GravyboxException):
    def __init__(self, query, upstream_api, upstream_status_code, upstream_content):
        message = "upstream api failure"
        super().__init__(message)
        logger.warning(message,
                       extra={"query": query,
                              "upstream_api": upstream_api,
                              "status_code": upstream_status_code,
                              "payload": upstream_content})


class UpstreamAPIServerCrash(GravyboxException):
    def __init__(self, query, upstream_api):
        message = "upstream api server crashed"
        super().__init__(message)
        logger.warning(message, extra={"query": query, "upstream_api": upstream_api})


class DataUnavailableFailure(GravyboxException):
    def __init__(self, query, upstream_api):
        message = "queried data is not available"
        super().__init__(message)
        logger.warning(message, extra={"query": query, "upstream_api": upstream_api})


class UnexpectedCondition(GravyboxException):
    def __init__(self, condition):
        message = "encountered unexpected condition"
        super().__init__(message)
        logger.warning(message, extra={"condition": condition})


class MalformedInput(GravyboxException):
    def __init__(self, malformed_input):
        message = "malformed input"
        super().__init__(message)
        logger.warning(message, extra={"malformed_input": malformed_input})
