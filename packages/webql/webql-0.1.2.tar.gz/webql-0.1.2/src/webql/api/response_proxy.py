import json
from typing import Generic, Union

from webql.common.errors import AttributeNotFoundError
from webql.syntax.node import ContainerListNode, ContainerNode, IdListNode, IdNode
from webql.web import InteractiveItemTypeT, WebDriver


class WQLResponseProxy(Generic[InteractiveItemTypeT]):
    def __init__(
        self,
        data: dict,
        web_driver: "WebDriver[InteractiveItemTypeT]",
        query_tree: ContainerNode,
    ):
        self._response_data = data
        self._web_driver = web_driver
        self._query_tree_node = query_tree

    def __getattr__(
        self, name
    ) -> Union["WQLResponseProxy[InteractiveItemTypeT]", InteractiveItemTypeT]:
        if self._response_data is None:
            raise AttributeError("Response data is None")
        if name not in self._response_data:
            raise AttributeNotFoundError(name, self._response_data)
        return self._resolve_item(
            self._response_data[name], self._query_tree_node.get_child_by_name(name)
        )

    def __getitem__(
        self, index: int
    ) -> Union[InteractiveItemTypeT, "WQLResponseProxy[InteractiveItemTypeT]"]:
        if not isinstance(self._response_data, list):
            raise ValueError("This node is not a list")
        return self._resolve_item(self._response_data[index], self._query_tree_node)

    def _resolve_item(
        self, item, query_tree_node
    ) -> Union[InteractiveItemTypeT, "WQLResponseProxy[InteractiveItemTypeT]"]:
        if isinstance(item, list):
            return WQLResponseProxy[InteractiveItemTypeT](item, self._web_driver, query_tree_node)

        if isinstance(query_tree_node, IdNode) or isinstance(query_tree_node, IdListNode):
            return self._web_driver.locate_interactive_element(item)

        return WQLResponseProxy[InteractiveItemTypeT](item, self._web_driver, query_tree_node)

    def __len__(self):
        if self._response_data is None:
            return 0
        return len(self._response_data)

    def __str__(self):
        return json.dumps(self._response_data, indent=2)

    def to_data(self) -> dict:
        """Converts the response data into a structured dictionary based on the query tree.

        Returns:
        dict: A structured dictionary representing the processed response data, with fact nodes replaced by name (values) from the response data.
        """
        return self._to_data_node(self._response_data, self._query_tree_node)

    def _to_data_node(self, response_data, query_tree_node) -> dict:
        if isinstance(query_tree_node, ContainerListNode):
            return self._to_data_container_list_node(response_data, query_tree_node)
        elif isinstance(query_tree_node, ContainerNode):
            return self._to_data_container_node(response_data, query_tree_node)
        elif isinstance(query_tree_node, IdListNode):
            return self._to_data_id_list_node(response_data)
        elif isinstance(query_tree_node, IdNode):
            return self._to_data_id_node(response_data)
        else:
            raise TypeError("Unsupported query tree node type")

    def _to_data_container_node(self, response_data: dict, query_tree_node: ContainerNode) -> dict:
        data_dict = {}
        for child_name, child_data in response_data.items():
            child_query_tree = query_tree_node.get_child_by_name(child_name)
            data_dict[child_name] = self._to_data_node(child_data, child_query_tree)
        return data_dict

    def _to_data_container_list_node(
        self, response_data: dict, query_tree_node: ContainerListNode
    ) -> list:
        return [self._to_data_container_node(item, query_tree_node) for item in response_data]

    def _to_data_id_node(self, response_data: dict) -> dict:
        name = response_data.get("name")
        if not name or not name.strip():
            name = self._web_driver.locate_interactive_element(response_data).text_content().strip()
        return name

    def _to_data_id_list_node(self, response_data: list) -> list:
        return [
            (
                item.get("name")
                if item.get("name") and item.get("name").strip()
                else self._web_driver.locate_interactive_element(item).text_content().strip()
            )
            for item in response_data
        ]
