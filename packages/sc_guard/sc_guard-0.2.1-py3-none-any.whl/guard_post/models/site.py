from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.site_attributes import SiteAttributes
    from ..models.site_key_type_0 import SiteKeyType0


T = TypeVar("T", bound="Site")


@_attrs_define
class Site:
    """
    Attributes:
        key (Union['SiteKeyType0', str]):
        site_id (int):
        name (str):
        field_id (Union[Any, Unset, str]): MongoDB document ObjectID
        key_id (Union[Any, Unset, str]):
        attributes (Union[Unset, SiteAttributes]):
        description (Union[Any, Unset, str]):
    """

    key: Union["SiteKeyType0", str]
    site_id: int
    name: str
    field_id: Union[Any, Unset, str] = UNSET
    key_id: Union[Any, Unset, str] = UNSET
    attributes: Union[Unset, "SiteAttributes"] = UNSET
    description: Union[Any, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.site_key_type_0 import SiteKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, SiteKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        site_id = self.site_id
        name = self.name
        field_id: Union[Any, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET

        else:
            field_id = self.field_id

        key_id: Union[Any, Unset, str]
        if isinstance(self.key_id, Unset):
            key_id = UNSET

        else:
            key_id = self.key_id

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
                "site_id": site_id,
                "name": name,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if key_id is not UNSET:
            field_dict["key_id"] = key_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.site_attributes import SiteAttributes
        from ..models.site_key_type_0 import SiteKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["SiteKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = SiteKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SiteKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        site_id = d.pop("site_id")

        name = d.pop("name")

        def _parse_field_id(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

        def _parse_key_id(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        key_id = _parse_key_id(d.pop("key_id", UNSET))

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, SiteAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = SiteAttributes.from_dict(_attributes)

        def _parse_description(data: object) -> Union[Any, Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        site = cls(
            key=key,
            site_id=site_id,
            name=name,
            field_id=field_id,
            key_id=key_id,
            attributes=attributes,
            description=description,
        )

        site.additional_properties = d
        return site

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
