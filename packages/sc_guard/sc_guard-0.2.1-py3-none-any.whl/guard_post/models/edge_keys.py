from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.edge_keys_end_type_0 import EdgeKeysEndType0
    from ..models.edge_keys_start_type_0 import EdgeKeysStartType0


T = TypeVar("T", bound="EdgeKeys")


@_attrs_define
class EdgeKeys:
    """
    Attributes:
        start (Union['EdgeKeysStartType0', str]):
        end (Union['EdgeKeysEndType0', str]):
    """

    start: Union["EdgeKeysStartType0", str]
    end: Union["EdgeKeysEndType0", str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.edge_keys_end_type_0 import EdgeKeysEndType0
        from ..models.edge_keys_start_type_0 import EdgeKeysStartType0

        start: Union[Dict[str, Any], str]

        if isinstance(self.start, EdgeKeysStartType0):
            start = self.start.to_dict()

        else:
            start = self.start

        end: Union[Dict[str, Any], str]

        if isinstance(self.end, EdgeKeysEndType0):
            end = self.end.to_dict()

        else:
            end = self.end

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start": start,
                "end": end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.edge_keys_end_type_0 import EdgeKeysEndType0
        from ..models.edge_keys_start_type_0 import EdgeKeysStartType0

        d = src_dict.copy()

        def _parse_start(data: object) -> Union["EdgeKeysStartType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                start_type_0 = EdgeKeysStartType0.from_dict(data)

                return start_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EdgeKeysStartType0", str], data)

        start = _parse_start(d.pop("start"))

        def _parse_end(data: object) -> Union["EdgeKeysEndType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                end_type_0 = EdgeKeysEndType0.from_dict(data)

                return end_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EdgeKeysEndType0", str], data)

        end = _parse_end(d.pop("end"))

        edge_keys = cls(
            start=start,
            end=end,
        )

        edge_keys.additional_properties = d
        return edge_keys

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
