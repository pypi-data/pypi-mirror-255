from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.edge import Edge





T = TypeVar("T", bound="Status")


@_attrs_define
class Status:
    """ Status model.

        Attributes:
            status (bool):
            edge (Union['Edge', Any, Unset]):
     """

    status: bool
    edge: Union['Edge', Any, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.edge import Edge
        status = self.status
        edge: Union[Any, Dict[str, Any], Unset]
        if isinstance(self.edge, Unset):
            edge = UNSET

        elif isinstance(self.edge, Edge):
            edge = UNSET
            if not isinstance(self.edge, Unset):
                edge = self.edge.to_dict()

        else:
            edge = self.edge



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "status": status,
        })
        if edge is not UNSET:
            field_dict["edge"] = edge

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.edge import Edge
        d = src_dict.copy()
        status = d.pop("status")

        def _parse_edge(data: object) -> Union['Edge', Any, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _edge_type_0 = data
                edge_type_0: Union[Unset, Edge]
                if isinstance(_edge_type_0,  Unset):
                    edge_type_0 = UNSET
                else:
                    edge_type_0 = Edge.from_dict(_edge_type_0)



                return edge_type_0
            except: # noqa: E722
                pass
            return cast(Union['Edge', Any, Unset], data)

        edge = _parse_edge(d.pop("edge", UNSET))


        status = cls(
            status=status,
            edge=edge,
        )

        status.additional_properties = d
        return status

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
