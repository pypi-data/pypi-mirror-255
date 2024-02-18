import json
import time
from enum import Enum
from typing import Union

from playwright.sync_api import Error, Frame, Locator, Page, sync_playwright

from webql.common.errors import (
    AccessibilityTreeError,
    ElementNotFoundError,
    NoOpenBrowserError,
    NoOpenPageError,
    OpenUrlError,
)
from webql.common.utils import ensure_url_scheme
from webql.web.driver_constants import USER_AGENT
from webql.web.network_monitor import PageActivityMonitor
from webql.web.web_driver import ScrollDirection, WebDriver

from .web_driver import WebDriver


class BrowserLoadState(Enum):
    DOMCONTENTLOADED = "domcontentloaded"
    """wait for the `DOMContentLoaded` event to be fired."""
    LOAD = "load"
    """wait for the `load` event to be fired."""
    NETWORKIDLE = "networkidle"
    """**DISCOURAGED** wait until there are no network connections for at least `500` ms."""


class PlaywrightWebDriver(WebDriver[Locator]):
    def __init__(self, headless=True) -> None:
        self._playwright = None

        self._browser = None
        """The current browser. Only use this to close the browser session in the end."""

        self._context = None
        """The current browser context. Use this to open a new page"""

        self._current_page = None
        """The current page that is being interacted with."""

        self._original_html = None
        """The page's original HTML content, prior to any WebQL modifications"""

        self._headless = headless
        """Whether to run browser in headless mode or not."""

        self._page_monitor = None

        self._current_tf_id = None

    def locate_interactive_element(self, response_data: dict) -> Locator:
        """
        Locates an interactive element in the web page.

        Parameters:

        response_data (dict): The data of the interactive element from the WebQL response.

        Returns:

        Locator: The interactive element.
        """
        tf623_id = response_data.get("tf623_id")
        if not tf623_id:
            raise ElementNotFoundError("tf623_id")
        iframe_path = response_data.get("attributes", {}).get("iframe_path")
        return self.find_element_by_id(tf623_id, iframe_path)

    def start_browser(self, user_session_extras: dict = None):
        """
        Starts a new browser session and set user session state (if there is any).
        """
        self._start_browser(headless=self._headless, user_session_extras=user_session_extras)

    def stop_browser(self):
        """Closes the current browser session."""
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def open_url(self, url: str):
        """
        Opens a new page and navigates to the given URL.
        """
        if not self._browser:
            raise NoOpenBrowserError()
        self._open_url(url)

    def get_current_url(self) -> str:
        """Get the URL of the active page."""
        if not self._current_page:
            raise NoOpenPageError()
        return self._current_page.url

    def get_html(self) -> dict:
        """Returns the original HTML (i.e. without any WebQL modifications) fetched from the most recently loaded page".

        Returns:

        string: The HTML content of the web page.
        """
        if not self._current_page:
            raise ValueError('No page is open. Make sure you call "open_url()" first.')
        return self._original_html

    def get_current_page(self) -> Page:
        """Returns the current page.

        Returns:

        Page: The current page.
        """
        if not self._current_page:
            raise ValueError('No page is open. Make sure you call "open_url()" first.')
        return self._current_page

    def open_html(self, html: str):
        """
        Opens a new page and loads the given HTML content.
        """
        if not self._browser:
            raise NoOpenBrowserError()
        self._current_page = self._context.new_page()
        self._current_tf_id = 0
        self._current_page.set_content(html)

    def prepare_accessiblity_tree(self, lazy_load_pages_count: int = 3) -> dict:
        """Prepare the AT by modifing the dom. It will return the accessibility tree after waiting for page to load and dom modification.

        Parameters:
        lazy_load_pages_count: The number of times to scroll down and up the page.

        Returns:
        dict: AT of the page
        """
        if not self._current_page:
            raise NoOpenPageError()

        self._original_html = self._current_page.content()
        self._preprocess_dom(lazy_load_pages_count=lazy_load_pages_count)

        accessibility_tree = None
        try:
            accessibility_tree = self._get_page_accessibility_tree(self._current_page)
            self._process_iframes(accessibility_tree)

        except Exception as e:
            raise AccessibilityTreeError() from e

        return accessibility_tree

    def get_accessibility_tree(self) -> dict:
        """Returns the up-to-date accessibility tree of the page.

        Returns:
        dict: The accessibility tree of the page.
        """
        try:
            accessibility_tree = self._get_page_accessibility_tree(self._current_page)
            self._process_iframes(accessibility_tree, modify_dom=False)
        except Exception as e:
            raise AccessibilityTreeError() from e

        return accessibility_tree

    def wait_for_page_ready_state(self):
        """Wait for the page to reach the "Page Ready" or stable state."""
        if not self._page_monitor:
            self._page_monitor = PageActivityMonitor()
            self._current_page.on("request", self._page_monitor.track_network_request)
            self._current_page.on("requestfinished", self._page_monitor.track_network_response)
            self._current_page.on("requestfailed", self._page_monitor.track_network_response)
            self._current_page.on("load", self._page_monitor.track_load)
        else:
            # Reset the network monitor to clear the logs
            self._page_monitor.reset()

        dom_listener_js = """
            (() => {
                const observer = new MutationObserver(mutations => {
                    const now = Date.now();
                    window.localStorage.setItem('lastDomChange', now);
                });
                observer.observe(document.body, { childList: true, subtree: true });
            })();
        """

        try:
            self._current_page.evaluate(dom_listener_js)
        # If the page is navigating, the evaluate function will raise an error. In this case, we wait for the page to load.
        except Error:
            start_time = time.time()
            while True:
                if self._page_monitor.get_load_status() or time.time() - start_time > 6:
                    break
                time.sleep(0.2)

        self._determine_load_state(self._page_monitor)

    def scroll_page(self, scroll_direction: ScrollDirection, pixels: int = 720):
        """Scrolls the page up or down.

        Parameters:
        scroll_direction (ScrollDirection): The direction to scroll the page.
        pixels (int): The number of pixels to scroll.
        """
        if not self._current_page:
            raise NoOpenPageError()

        delta_y = pixels if scroll_direction == ScrollDirection.DOWN else -pixels
        self._current_page.mouse.wheel(delta_x=0, delta_y=delta_y)

    def scroll_to_bottom(self):
        """Scrolls the page to the bottom."""
        if not self._current_page:
            raise NoOpenPageError()

        scroll_js = """async () => {
            const viewportHeight = window.document.documentElement.clientHeight;
            const totalHeight = window.document.documentElement.scrollHeight;
            let scrolledHeight = window.scrollY;

            while (scrolledHeight < totalHeight) {
                scrolledHeight += viewportHeight;
                window.scrollTo(0, scrolledHeight);
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }"""
        self._current_page.evaluate(scroll_js)

    def _process_iframes(
        self,
        page_accessibility_tree: dict = None,
        *,
        iframe_path: str = "",
        frame: Frame = None,
        modify_dom: bool = True,
    ):
        """
        Recursively retrieves the accessibility trees for all iframes in a page or frame.

        Parameters:
            iframe_path (str): The path of the iframe in the frame hierarchy.
            frame (Frame): The frame object representing the current frame.
            page_accessibility_tree (dict): The accessibility tree of the page.

        Returns:
            None
        """
        if frame is None:
            iframes = self._current_page.query_selector_all("iframe")
        else:
            iframes = frame.content_frame().query_selector_all("iframe")

        for iframe in iframes:
            iframe_id = iframe.get_attribute("tf623_id")
            iframe_path_to_send = ""
            if iframe_path:
                iframe_path_to_send = f"{iframe_path}."
            iframe_path_to_send = f"{iframe_path_to_send}{iframe_id}"
            iframe_accessibility_tree = self._get_frame_accessibility_tree(
                iframe, iframe_path_to_send, modify_dom=modify_dom
            )

            self._merge_iframe_tree_into_page(
                iframe_id, page_accessibility_tree, iframe_accessibility_tree
            )

            self._process_iframes(
                iframe_path=iframe_path_to_send,
                frame=iframe,
                page_accessibility_tree=page_accessibility_tree,
                modify_dom=modify_dom,
            )

    def _get_page_accessibility_tree(self, page: Page) -> dict:
        """
        Retrieves the accessibility tree for the given page.

        Returns:
            dict: The accessibility tree for the page.
        """
        return page.accessibility.snapshot(interesting_only=False)

    def _get_frame_accessibility_tree(
        self, frame: Frame, iframe_path, modify_dom: bool = True
    ) -> dict:
        """
        Retrieves the accessibility tree for a given frame.

        Parameters:
            frame (Frame): The frame for which to retrieve the accessibility tree.
            iframe_path: The path of the iframe within the frame.

        Returns:
            dict: The accessibility tree for the frame.
        """
        frame_context = frame.content_frame()

        # Prevent modify dom multiple times when getting the most up-to-date accessibility tree
        if modify_dom:
            self._modify_dom(context=frame_context, iframe_path=iframe_path)

        content_frame_document_serialized = frame_context.evaluate(
            self._get_serialized_dom_js_code()
        )
        temp_browser = self._playwright.chromium.launch()
        temp_page = temp_browser.new_page()
        # temp_page.route("**/*", lambda route: route.abort())
        temp_page.set_content(content_frame_document_serialized)
        temp_page.wait_for_load_state("load")
        accessibility_tree = self._get_page_accessibility_tree(temp_page)
        temp_browser.close()

        return accessibility_tree

    def _merge_iframe_tree_into_page(
        self, iframe_id, accessibility_tree: dict, iframe_accessibility_tree: dict
    ):
        """
        Stitches the iframe accessibility tree with the page accessibility tree.

        Parameters:
            iframe_id (str): The ID of the iframe.
            accessibility_tree (dict): The accessibility tree of the page.
            iframe_accessibility_tree (dict): The accessibility tree of the iframe.

        Returns:
            None
        """
        for child in accessibility_tree.get("children", []):
            keyshortcuts_str = child.get("keyshortcuts", "{}")
            keyshortcuts_dict = json.loads(keyshortcuts_str)
            if "children" not in child:
                child["children"] = []
            if "tf623_id" in keyshortcuts_dict and keyshortcuts_dict["tf623_id"] == iframe_id:
                child["children"].append(iframe_accessibility_tree)
                break
            self._merge_iframe_tree_into_page(iframe_id, child, iframe_accessibility_tree)

    def _preprocess_dom(self, lazy_load_pages_count=3):
        """Scroll the page and Modifies the dom by assigning a unique ID to every node in the document.

        Parameters:
        lazy_load_pages_count (int): The number of pages to scroll down and up to load lazy loaded content.
        """
        if not self._current_page:
            raise NoOpenPageError()

        self._page_scroll(pages=lazy_load_pages_count)
        self._modify_dom(context=self._current_page)

    def _open_url(self, url: str):
        """Opens a new page and navigates to the given URL. Initialize the storgage state if provided.

        Parameters:

        url (str): The URL to navigate to.
        storgate_state_content (optional): The storage state with which user would like to initialize the browser.

        """

        self._current_page = None
        url = ensure_url_scheme(url)

        try:
            page = self._context.new_page()
            self._current_tf_id = 0
            page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            raise OpenUrlError() from e

        self._current_page = page

    def _get_modify_dom_and_update_current_tf_id_js_code(self) -> str:
        """Returns the JavaScript code that is used to modify the DOM adn return the updated current_tf_id."""
        # Future scope: Move to a js file, read it and return it
        return """
            ({ iframe_path, current_tf_id }) => {
              WebQL_IDGenerator = class {
                constructor() {
                  this.currentID = current_tf_id || 0;
                }

                getNextID() {
                  this.currentID += 1;
                  return this.currentID;
                }
              };

              const _tf_id_generator = new window.WebQL_IDGenerator();

              function extractAttributes(node) {
                const attributes = { html_tag: node.nodeName.toLowerCase() };
                const skippedAttributes = ['style', 'srcdoc'];

                for (let i = 0; i < node.attributes.length; i++) {
                  const attribute = node.attributes[i];
                  if (!attribute.specified || !skippedAttributes.includes(attribute.name)) {
                    attributes[attribute.name] = attribute.value.slice(0, 100) || true;
                  }
                }

                return attributes;
              }

              function pre_process_dom_node(node) {
                if (!node) {
                  return;
                }
                if (node.hasAttribute('aria-keyshortcuts')) {
                  try {
                    ariaKeyShortcuts = JSON.parse(node.getAttribute('aria-keyshortcuts'));
                    if (ariaKeyShortcuts.hasOwnProperty('html_tag')) {
                      if (ariaKeyShortcuts.hasOwnProperty('aria-keyshortcuts')) {
                        ariaKeyShortcutsInsideAriaKeyShortcuts =
                          ariaKeyShortcuts['aria-keyshortcuts'];
                        node.setAttribute(
                          'aria-keyshortcuts',
                          ariaKeyShortcutsInsideAriaKeyShortcuts
                        );
                      } else {
                        node.removeAttribute('aria-keyshortcuts');
                      }
                    }
                  } catch (e) {
                    //aria-keyshortcuts is not a valid json, proceed with current aria-keyshortcuts value
                  }
                }

                let currentChildNodes = node.childNodes;
                if (node.shadowRoot) {
                    const childrenNodeList = Array.from(node.shadowRoot.children);

                    if (childrenNodeList.length > 0) {
                        currentChildNodes = Array.from(childrenNodeList);
                    } else if (node.shadowRoot.textContent.trim() !== '') {
                        node.setAttribute('aria-label', node.shadowRoot.textContent.trim());
                    }
                } else if (node.tagName === 'SLOT') {
                    currentChildNodes = node.assignedNodes({ flatten: true });
                }

                tfId = _tf_id_generator.getNextID();

                node.setAttribute('tf623_id', tfId);

                if (iframe_path) {
                    node.setAttribute('iframe_path', iframe_path);
                }
                node.setAttribute(
                    'aria-keyshortcuts',
                    JSON.stringify(extractAttributes(node))
                );

                const childNodes = Array.from(currentChildNodes).filter((childNode) => {
                  return (
                    childNode.nodeType === Node.ELEMENT_NODE ||
                    (childNode.nodeType === Node.TEXT_NODE &&
                      childNode.textContent.trim() !== '')
                  );
                });
                for (let i = 0; i < childNodes.length; i++) {
                  let childNode = childNodes[i];
                  if (childNode.nodeType === Node.TEXT_NODE) {
                    const text = childNode.textContent.trim();
                    if (text) {
                      if (childNodes.length > 1) {
                        const span = document.createElement('span');
                        span.textContent = text;
                        node.insertBefore(span, childNode);
                        node.removeChild(childNode);
                        childNode = span;
                      } else if (!node.hasAttribute('aria-label')) {
                        const structureTags = [
                          'a',
                          'button',
                          'h1',
                          'h2',
                          'h3',
                          'h4',
                          'h5',
                          'h6',
                          'script',
                          'style',
                        ];
                        if (!structureTags.includes(node.nodeName.toLowerCase())) {
                          node.setAttribute('aria-label', text);
                        }
                      }
                    }
                  }
                  if (childNode.nodeType === Node.ELEMENT_NODE) {
                    pre_process_dom_node(childNode);
                  }
                }
              }
              pre_process_dom_node(document.documentElement);
              return _tf_id_generator.currentID;
            };
        """

    def _get_serialized_dom_js_code(self) -> str:
        """Returns the serialized DOM."""
        return "() => { return new XMLSerializer().serializeToString(document); }"

    def _modify_dom(self, context: Union[Page, Frame], iframe_path=None):
        """
        Modifies the DOM and updates the current_tf_id.

        Parameters:
            context (Page | Frame): The context in which the DOM will be modified.
            iframe_path (str, optional): The path to the iframe. Defaults to None.
        """
        self._current_tf_id = context.evaluate(
            self._get_modify_dom_and_update_current_tf_id_js_code(),
            {"iframe_path": iframe_path, "current_tf_id": self._current_tf_id},
        )

    def _page_scroll(self, pages=3):
        """Scrolls the page down first and then up to load all contents on the page.

        Parameters:

        pages (int): The number of pages to scroll down.
        """
        if pages < 1:
            return

        delta_y = 10000
        for _ in range(pages):
            self._current_page.mouse.wheel(delta_x=0, delta_y=delta_y)
            time.sleep(0.1)

        delta_y = -10000
        time.sleep(1)
        for _ in range(pages):
            self._current_page.mouse.wheel(delta_x=0, delta_y=delta_y)
            time.sleep(0.1)

    def _start_browser(self, user_session_extras: dict = None, headless=True, load_media=False):
        """Starts a new browser session and set storage state (if there is any).

        Parameters:

        user_session_extras (optional): the JSON object that holds user session information
        headless (bool): Whether to start the browser in headless mode.
        load_media (bool): Whether to load media (images, fonts, etc.) or not.
        """
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._current_tf_id = 0
        self._context = self._browser.new_context(
            user_agent=USER_AGENT, storage_state=user_session_extras
        )
        # Block requests for unnecessary resources if in headless mode and load_media is False
        if not load_media and headless:
            self._context.route(
                "**/*",
                lambda route, request: (
                    route.abort()
                    if request.resource_type in ["image", "media", "font"]
                    else route.continue_()
                ),
            )

    def _get_frame_context(self, iframe_path: str = None) -> Union[Frame, Page]:
        """
        Returns the frame context for the given iframe path.

        Parameters:
            iframe_path (str): The path of the iframe within the frame.

        Returns:
            Frame | Page: The frame context for the given iframe path.
        """
        if not iframe_path:
            return self._current_page
        iframe_path_list = iframe_path.split(".")
        frame_context = self._current_page
        for iframe_id in iframe_path_list:
            frame_context = frame_context.frame_locator(f"[tf623_id='{iframe_id}']")
        return frame_context

    def find_element_by_id(self, tf623_id: str, iframe_path: str = None) -> Locator:
        """
        Finds an element by its TF ID within a specified iframe.

        Args:
            tf623_id (str): The generated tf id of the element to find.
            iframe_path (str): The path to the iframe containing the element.

        Returns:
            Locator: The located element.

        Raises:
            ElementNotFoundError: If the element with the specified TF ID is not found.
        """
        try:
            element_frame_context = self._get_frame_context(iframe_path)
            return element_frame_context.locator(f"[tf623_id='{tf623_id}']")
        except Exception as e:
            raise ElementNotFoundError(tf623_id) from e

    def _determine_load_state(self, monitor: PageActivityMonitor, timeout_seconds=14):
        start_time = time.time()

        while True:
            try:
                last_updated_timestamp = self._current_page.evaluate(
                    """() => window.localStorage.getItem('lastDomChange')"""
                )
            # If the page is navigating, the evaluate function will raise an error. In this case, we wait for the page to load.
            except Error:
                while True:
                    if self._page_monitor.get_load_status() or time.time() - start_time > 6:
                        break
                    time.sleep(0.2)

            if monitor.check_conditions(last_active_dom_time=last_updated_timestamp):
                break
            if time.time() - start_time > timeout_seconds:
                break
            time.sleep(0.3)
