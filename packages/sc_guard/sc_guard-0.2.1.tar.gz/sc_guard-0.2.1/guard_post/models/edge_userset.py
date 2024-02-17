from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EdgeUserset")


@_attrs_define
class EdgeUserset:
    """
    Attributes:
        start (Union[Any, Unset, str]):
        end (Union[Any, Unset, str]):
    """

    start: Union[Any, Unset, str] = UNSET
    end: Union[Any, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start: Union[Any, Unset, str]
        if isinstance(self.start, Unset):
            start = UNSET

        else:
            start = self.start

        end: Union[Any, Unset, str]
        if isinstance(self.end, Unset):
            end = UNSET

        else:
            end = self.end

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_start(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        start = _parse_start(d.pop("start", UNSET))

        def _parse_end(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        end = _parse_end(d.pop("end", UNSET))

        edge_userset = cls(
            start=start,
            end=end,
        )

        edge_userset.additional_properties = d
        return edge_userset

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
