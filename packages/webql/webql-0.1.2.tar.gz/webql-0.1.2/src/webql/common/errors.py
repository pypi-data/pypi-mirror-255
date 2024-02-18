import json
import logging

# pylint: disable-all
WEBQL_1000_API_KEY_ERROR = 1000
WEBQL_1001_ATTRIBUTE_NOT_FOUND_ERROR = 1001
WEBQL_1002_NO_OPEN_BROWSER_ERROR = 1002
WEBQL_1003_NO_OPEN_PAGE_ERROR = 1003
WEBQL_1004_PAGE_TIMEOUT_ERROR = 1004
WEBQL_1005_ACCESSIBILITY_TREE_ERROR = 1005
WEBQL_1006_ELEMENT_NOT_FOUND_ERROR = 1006
WEBQL_1007_OPEN_URL_ERROR = 1007
WEBQL_1008_CLICK_ERROR = 1008
WEBQL_1009_INPUT_ERROR = 1009
WEBQL_1010_QUERY_SYNTAX_ERROR = 1010
WEBQL_1011_UNABLE_TO_CLOSE_POPUP_ERROR = 1011
WEBQL_2000_SERVER_ERROR = 2000
WEBQL_2001_SERVER_TIMEOUT_ERROR = 2001


class BaseWebQLError(Exception):
    def __init__(self, error, error_code):
        self.error = error
        self.error_code = error_code

    def __str__(self):
        return f"{self.error_code} {self.__class__.__name__}: {self.error}"


class APIKeyError(BaseWebQLError):
    def __init__(
        self,
        message="Invalid or missing API key. Please set the environment variable 'WEBQL_API_KEY' with a valid API key.",
    ):
        super().__init__(message, WEBQL_1000_API_KEY_ERROR)


class AttributeNotFoundError(BaseWebQLError):
    def __init__(self, name, response_data):
        message = f"{name} not found in WebQL response node: {json.dumps(response_data)[:300]}. If you are trying to perform an action on an element, make sure the element is the leaf node in your query."
        super().__init__(message, WEBQL_1001_ATTRIBUTE_NOT_FOUND_ERROR)


class NoOpenBrowserError(BaseWebQLError):
    def __init__(
        self,
        message='No open browser if detected. Make sure you call "start_browser()" first.',
    ):
        super().__init__(message, WEBQL_1002_NO_OPEN_BROWSER_ERROR)


class NoOpenPageError(BaseWebQLError):
    def __init__(self, message='No page is open. Make sure you call "open_url()" first.'):
        super().__init__(message, WEBQL_1003_NO_OPEN_PAGE_ERROR)


class PageTimeoutError(BaseWebQLError):
    def __init__(self, message="Page took too long to respond"):
        super().__init__(message, WEBQL_1004_PAGE_TIMEOUT_ERROR)


class AccessibilityTreeError(BaseWebQLError):
    def __init__(self, message="Error generating accessibility tree"):
        super().__init__(message, WEBQL_1005_ACCESSIBILITY_TREE_ERROR)


class ElementNotFoundError(BaseWebQLError):
    def __init__(self, element_id=None):
        if element_id:
            message = f"{element_id} not found in WebQL response node."
        else:
            message = "Element not found in WebQL response node."
        super().__init__(message, WEBQL_1006_ELEMENT_NOT_FOUND_ERROR)


class OpenUrlError(BaseWebQLError):
    def __init__(self, message="Unable to open url"):
        super().__init__(message, WEBQL_1007_OPEN_URL_ERROR)


class ClickError(BaseWebQLError):
    def __init__(self, message="Unable to click"):
        super().__init__(message, WEBQL_1008_CLICK_ERROR)


class InputError(BaseWebQLError):
    def __init__(self, message="Unable to input text"):
        super().__init__(message, WEBQL_1009_INPUT_ERROR)


class QuerySyntaxError(BaseWebQLError):
    def __init__(self, message=None, *, unexpected_token, row, column):
        if not message:
            message = f"Unexpected character {unexpected_token} at row {row}, column {column} in WebQL query."
        super().__init__(message, WEBQL_1010_QUERY_SYNTAX_ERROR)
        self.unexpected_token = unexpected_token
        self.row = row
        self.column = column


class UnableToClosePopupError(BaseWebQLError):
    def __init__(
        self,
        message="Failed to automatically close popup. Call accessibility_tree() if you would like to analyze the popup and manually close it.",
    ):
        super().__init__(message, WEBQL_1011_UNABLE_TO_CLOSE_POPUP_ERROR)


class WebQLServerError(BaseWebQLError):
    def __init__(self, error=None, error_code=None):
        if error is None:
            error = (
                "WebQL server error, please try again, if this persists, please reach out to us."
            )
        if error_code is None:
            error_code = WEBQL_2000_SERVER_ERROR

        super().__init__(error, error_code)


class WebQLServerTimeoutError(WebQLServerError):
    def __init__(
        self,
        message="Webql Server Timed Out, please try again, if this persists, please reach out to us.",
    ):
        super().__init__(message, WEBQL_2001_SERVER_TIMEOUT_ERROR)
