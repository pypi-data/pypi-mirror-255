"""
This module is an entrypoint to WebQL service
"""

import logging

from webql.web import InteractiveItemTypeT, PlaywrightWebDriver, WebDriver

from .session import Session

log = logging.getLogger(__name__)


def start_session(
    url: str,
    *,
    web_driver: WebDriver[InteractiveItemTypeT] = PlaywrightWebDriver(),
) -> Session[InteractiveItemTypeT]:
    """Start a new WebQL session.

    Parameters:

    url (str): The URL to start the session with.
    web_driver (optional): The web driver to use. Defaults to Playwright web driver.

    Returns:

    Session: The new session.
    """
    log.debug(f"Starting session with {url}")

    web_driver.start_browser()
    web_driver.open_url(url)
    session = Session[InteractiveItemTypeT](web_driver)
    return session
