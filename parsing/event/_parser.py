import os

from selenium import webdriver


def get_event_page(self, path: str = None, return_page: bool = False):
    """
    Method collects main page for an event.
    :param path: saves the page to the absolute path if specified
    :param return_page: returns page if True
    """

    dr = webdriver.Chrome()
    link = self.get_event_link()
    dr.get(link)
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(dr.page_source)
    if return_page:
        return dr.page_source
