from html.parser import HTMLParser
from typing import Callable, List, Tuple


class BasicHtmlParser(HTMLParser):
    """
    BasicHtmlParser

    Simple class to match starttags against target_tag and target_attribute.

    :target_tag: Target tag.
    :target_attribute: Target attribute.
    :predicate: (Optional) A tuple of functions to filter the target_tag,
                they are mapped according to the position of target_attribute:
                func1=target_att[0] func2=target_att[1]
    """

    def __init__(
        self,
        target_tag: str,
        target_attribute: Tuple[str, str | None],
        predicate: Tuple[Callable[..., bool] | None, Callable[..., bool] | None] | None = None
    ):
        super().__init__()

        self._target_tag: str                                                                   = target_tag
        self._target_attribute: Tuple[str, str | None]                                          = target_attribute
        self._attribute: str                                                                    = ""
        self._found: bool                                                                       = False
        self._predicate: Tuple[Callable[..., bool] | None, Callable[..., bool] | None] | None   = predicate

        assert self._target_tag != "", "target_tag cannot be empty."
        assert self._target_attribute[0] != "", "target_attribute name cannot be empty."


    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        """
        handle_starttag

        Handles start tags.

        :tag: Tag name.
        :attrs: List of attributes.
        :return:
        """

        if self._found: return
        if not tag == self._target_tag: return

        for k, v in attrs:
            if not k == self._target_attribute[0]: continue
            if not v: continue
            if self._predicate and self._predicate[0] and not self._predicate[0](k): continue
            if self._predicate and self._predicate[1] and not self._predicate[1](v): continue

            self._attribute = v
            self._found = True

            return


    def get_attribute(self) -> str:
        """
        get_attribute

        Gets the specific attribute of html document.

        :return: The attribute if it was found or an empty string if it wasn't.
        """

        return self._attribute

