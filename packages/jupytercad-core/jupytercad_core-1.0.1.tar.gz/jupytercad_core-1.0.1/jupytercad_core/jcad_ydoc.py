import json
from typing import Any, Callable
from functools import partial

import y_py as Y
from jupyter_ydoc.ybasedoc import YBaseDoc


class YJCad(YBaseDoc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ysource = self._ydoc.get_text("source")
        self._yobjects = self._ydoc.get_array("objects")
        self._yoptions = self._ydoc.get_map("options")
        self._ymeta = self._ydoc.get_map("metadata")
        self._youtputs = self._ydoc.get_map("outputs")

    def version(self) -> str:
        return "0.1.0"

    def get(self) -> str:
        """
        Returns the content of the document.
        :return: Document's content.
        :rtype: Any
        """
        objects = json.loads(self._yobjects.to_json())
        options = json.loads(self._yoptions.to_json())
        meta = json.loads(self._ymeta.to_json())
        outputs = json.loads(self._youtputs.to_json())
        return json.dumps(
            dict(objects=objects, options=options, metadata=meta, outputs=outputs),
            indent=2,
        )

    def set(self, value: str) -> None:
        """
        Sets the content of the document.
        :param value: The content of the document.
        :type value: Any
        """
        valueDict = json.loads(value)
        newObj = []
        for obj in valueDict["objects"]:
            newObj.append(Y.YMap(obj))
        with self._ydoc.begin_transaction() as t:
            length = len(self._yobjects)
            self._yobjects.delete_range(t, 0, length)
            # workaround for https://github.com/y-crdt/ypy/issues/126:
            # self._yobjects.extend(t, newObj)
            for o in newObj:
                self._yobjects.append(t, o)

            self._replace_y_map(t, self._yoptions, valueDict["options"])
            self._replace_y_map(t, self._ymeta, valueDict["metadata"])
            self._replace_y_map(t, self._youtputs, valueDict.get("outputs", {}))

    def observe(self, callback: Callable[[str, Any], None]):
        self.unobserve()
        self._subscriptions[self._ystate] = self._ystate.observe(
            partial(callback, "state")
        )
        self._subscriptions[self._ysource] = self._ysource.observe(
            partial(callback, "source")
        )
        self._subscriptions[self._yobjects] = self._yobjects.observe_deep(
            partial(callback, "objects")
        )
        self._subscriptions[self._yoptions] = self._yoptions.observe_deep(
            partial(callback, "options")
        )
        self._subscriptions[self._ymeta] = self._ymeta.observe_deep(
            partial(callback, "meta")
        )

    def _replace_y_map(self, t: Y.YTransaction, y_map: Y.YMap, new_value: dict):
        for key in y_map:
            y_map.pop(t, key)
        y_map.update(t, new_value.items())
