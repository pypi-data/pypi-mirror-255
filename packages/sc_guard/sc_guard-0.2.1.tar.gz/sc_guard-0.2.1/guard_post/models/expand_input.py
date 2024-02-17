from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.expand_input_key_type_0 import ExpandInputKeyType0


T = TypeVar("T", bound="ExpandInput")


@_attrs_define
class ExpandInput:
    """Input for the expand operation

    Attributes:
        key (Union['ExpandInputKeyType0', str]):
        relation (str):
    """

    key: Union["ExpandInputKeyType0", str]
    relation: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.expand_input_key_type_0 import ExpandInputKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, ExpandInputKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        relation = self.relation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "relation": relation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.expand_input_key_type_0 import ExpandInputKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["ExpandInputKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = ExpandInputKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ExpandInputKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        relation = d.pop("relation")

        expand_input = cls(
            key=key,
            relation=relation,
        )

        expand_input.additional_properties = d
        return expand_input

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
