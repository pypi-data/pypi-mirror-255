from enum import Enum
from typing import TypeVar

from typing_extensions import Protocol

InteractiveItemTypeT = TypeVar("InteractiveItemTypeT")


class ScrollDirection(Enum):
    UP = 1
    DOWN = 2


class WebDriver(Protocol[InteractiveItemTypeT]):
    def locate_interactive_element(self, response_data: dict) -> InteractiveItemTypeT:
        """
        Locates an interactive element in the web page.

        Parameters:

        response_data (dict): The data of the interactive element from the WebQL response.

        Returns:

        InteractiveItemTypeT: The interactive element.
        """

    def start_browser(self, user_session_extras: dict = None):
        """Start the browser.

        Parameters:

        user_session_extras (optional): the JSON object that holds user session information
        """

    def stop_browser(self):
        """Stops/closes the browser."""

    def open_url(self, url: str):
        """Open URL in the browser."""

    def get_current_url(self) -> str:
        """Get the URL of the active page."""

    def prepare_accessiblity_tree(self, lazy_load_pages_count: int) -> dict:
        """Prepare the AT by modifing the dom. It will return the accessibility tree after preparation.

        Parameters:
        lazy_load_pages_count: The number of times to scroll down and up the page.

        Returns:
        dict: AT of the page
        """

    def get_accessibility_tree(self) -> dict:
        """Returns the up-to-date accessibility tree of the page.

        Returns:
        dict: The accessibility tree of the page.
        """

    def wait_for_page_ready_state(self):
        """Wait for the page to reach the "Page Ready" or stable state."""

    def get_html(self) -> dict:
        """Returns the original HTML (i.e. without any WebQL modifications) fetched from the most recently loaded page".

        Returns:

        string: The HTML content of the web page.
        """

    def scroll_page(self, scroll_direction: ScrollDirection, pixels: int = 720):
        """Scrolls the page up or down.

        Parameters:
        scroll_direction (ScrollDirection): The direction to scroll the page.
        pixels (int): The number of pixels to scroll.
        """

    def scroll_to_bottom(self):
        """Scrolls the page to the bottom."""
