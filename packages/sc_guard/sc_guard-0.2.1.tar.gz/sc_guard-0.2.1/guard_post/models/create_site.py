from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_site_attributes import CreateSiteAttributes
    from ..models.create_site_key_type_0 import CreateSiteKeyType0


T = TypeVar("T", bound="CreateSite")


@_attrs_define
class CreateSite:
    """
    Attributes:
        key (Union['CreateSiteKeyType0', str]):
        name (str):
        site_id (int):
        attributes (Union[Unset, CreateSiteAttributes]):
        description (Union[Any, Unset, str]):
    """

    key: Union["CreateSiteKeyType0", str]
    name: str
    site_id: int
    attributes: Union[Unset, "CreateSiteAttributes"] = UNSET
    description: Union[Any, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_site_key_type_0 import CreateSiteKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, CreateSiteKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        name = self.name
        site_id = self.site_id
        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        description: Union[Any, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET

        else:
            description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "name": name,
                "site_id": site_id,
            }
        )
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_site_attributes import CreateSiteAttributes
        from ..models.create_site_key_type_0 import CreateSiteKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["CreateSiteKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = CreateSiteKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CreateSiteKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        name = d.pop("name")

        site_id = d.pop("site_id")

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, CreateSiteAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = CreateSiteAttributes.from_dict(_attributes)

        def _parse_description(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        create_site = cls(
            key=key,
            name=name,
            site_id=site_id,
            attributes=attributes,
            description=description,
        )

        create_site.additional_properties = d
        return create_site

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
