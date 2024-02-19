from tkinter import Text
from typing import Callable

from pih.const import CONST

class BarcodeInput(Text):

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.result_handler: Callable[[str, bool], None] | None = None
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.internal_set: bool = False

        def onModification(event) -> None:
            if not self.internal_set:
                content = event.widget.get("1.0", "end-1c")
                next: int = content.find(BARCODE_READER.PREFIX)
                if next > 0:
                    content = content[next:]
                if len(content) > 0:
                    if content[0] == BARCODE_READER.PREFIX and content[-1] == BARCODE_READER.SUFFIX:
                        self.result_handler(
                            content[len(BARCODE_READER.PREFIX):-len(BARCODE_READER.SUFFIX)])
                    elif content[0] != BARCODE_READER.PREFIX:
                        self.center()
                        self.result_handler(content, False)
                else:
                    self.result_handler(content, False)

        def onEnter(event) -> None:
            content = event.widget.get("1.0", "end-1c")
            self.result_handler(content, True)
            self.set_text("")

        self.bind("<<TextModified>>", onModification)
        self.bind('<Return>', onEnter)


    def set_result_handler(self, value: Callable) -> None:
        self.result_handler = value

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")
        return result

    def set_text(self, value: str) -> None:
        self.internal_set = True
        self.delete(1.0, "end")
        self.insert(1.0, value)
        self.center()
        self.internal_set = False

    def center(self) -> None:
        self.tag_configure("tag_name", justify='center')
        self.tag_add("tag_name", "1.0", "end")
