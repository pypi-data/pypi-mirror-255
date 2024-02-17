from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.edge_keys import EdgeKeys
    from ..models.edge_userset import EdgeUserset


T = TypeVar("T", bound="EdgeInput")


@_attrs_define
class EdgeInput:
    """RelationKey model.

    Attributes:
        keys (EdgeKeys):
        relation (str):
        userset (Union[Unset, EdgeUserset]):
    """

    keys: "EdgeKeys"
    relation: str
    userset: Union[Unset, "EdgeUserset"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        keys = self.keys.to_dict()

        relation = self.relation
        userset: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.userset, Unset):
            userset = self.userset.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "keys": keys,
                "relation": relation,
            }
        )
        if userset is not UNSET:
            field_dict["userset"] = userset

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.edge_keys import EdgeKeys
        from ..models.edge_userset import EdgeUserset

        d = src_dict.copy()
        keys = EdgeKeys.from_dict(d.pop("keys"))

        relation = d.pop("relation")

        _userset = d.pop("userset", UNSET)
        userset: Union[Unset, EdgeUserset]
        if isinstance(_userset, Unset):
            userset = UNSET
        else:
            userset = EdgeUserset.from_dict(_userset)

        edge_input = cls(
            keys=keys,
            relation=relation,
            userset=userset,
        )

        edge_input.additional_properties = d
        return edge_input

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
