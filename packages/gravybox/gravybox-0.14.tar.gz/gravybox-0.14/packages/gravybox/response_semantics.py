from gravybox.betterstack import collect_logger

logger = collect_logger()


class Response:
    def __init__(self, status_code, success, content, error):
        self.status_code = status_code
        self.success = success
        self.content = content
        self.error = error

    def __eq__(self, other):
        return self.status_code == other.status_code \
            and self.success == other.success \
            and self.content == other.content \
            and self.error == other.error

    def __repr__(self):
        return f"Response(<{self.status_code}> | success: {self.success} | content: {self.content} | error: " \
               f"{self.error})"

    def flaskify(self):
        return {
            "success": self.success,
            "error": self.error,
            "content": self.content
        }, self.status_code


def create_response(content):
    response = Response(
        status_code=200,
        success=True,
        content=content,
        error=""
    )
    logger.info("returning success response", extra={"payload": response.flaskify()[0], "status_code": 200})
    return response


def create_all_apis_failed_response(failed_query):
    return create_error_response(515, f"all upstream apis failed for query: {failed_query}")


def create_error_response(status_code, error):
    response = Response(
        status_code=status_code,
        success=False,
        content={},
        error=error
    )
    logger.info("returning failure response", extra={"payload": response.flaskify()[0], "status_code": status_code})
    return response
