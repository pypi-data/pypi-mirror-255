from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.list_objects_input_key_key import ListObjectsInputKeyKey


T = TypeVar("T", bound="ListObjectsInputKey")


@_attrs_define
class ListObjectsInputKey:
    """Use key to identify user

    Attributes:
        key (ListObjectsInputKeyKey):
        relation (str):
        type (str):
    """

    key: Dict[str, Any]
    relation: str
    type: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        if not isinstance(self.key, Dict):
            key = self.key.to_dict()
        else:
            key = self.key
        relation = self.relation
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "relation": relation,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_objects_input_key_key import ListObjectsInputKeyKey

        d = src_dict.copy()
        key = ListObjectsInputKeyKey.from_dict(d.pop("key"))

        relation = d.pop("relation")

        type = d.pop("type")

        list_objects_input_key = cls(
            key=key,
            relation=relation,
            type=type,
        )

        list_objects_input_key.additional_properties = d
        return list_objects_input_key

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
