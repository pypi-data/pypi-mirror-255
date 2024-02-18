def ensure_url_scheme(url):
    """
    Ensure that the URL has a scheme.
    """
    if not url.startswith(("http://", "https://", "file://")):
        return "https://" + url
    return url


def close_all_popups_handler(popups: list):
    """This is a handler function for popups. Passing it as the callback function into session.on("popup") method will close all popups.

    Parameters:

    popups(list): The list containing popup objects.
    """
    for popup in popups:
        popup.close()
