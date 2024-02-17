from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_org_attributes import CreateOrgAttributes
    from ..models.create_org_key_type_0 import CreateOrgKeyType0


T = TypeVar("T", bound="CreateOrg")


@_attrs_define
class CreateOrg:
    """
    Attributes:
        key (Union['CreateOrgKeyType0', str]):
        name (str):
        description (Union[Any, Unset, str]):
        attributes (Union[Unset, CreateOrgAttributes]):
    """

    key: Union["CreateOrgKeyType0", str]
    name: str
    description: Union[Any, Unset, str] = UNSET
    attributes: Union[Unset, "CreateOrgAttributes"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_org_key_type_0 import CreateOrgKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, CreateOrgKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        name = self.name
        description: Union[Any, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET

        else:
            description = self.description

        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_org_attributes import CreateOrgAttributes
        from ..models.create_org_key_type_0 import CreateOrgKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["CreateOrgKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = CreateOrgKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CreateOrgKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        name = d.pop("name")

        def _parse_description(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, CreateOrgAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = CreateOrgAttributes.from_dict(_attributes)

        create_org = cls(
            key=key,
            name=name,
            description=description,
            attributes=attributes,
        )

        create_org.additional_properties = d
        return create_org

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
