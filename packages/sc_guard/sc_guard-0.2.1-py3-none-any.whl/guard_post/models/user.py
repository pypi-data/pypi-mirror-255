from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_attributes import UserAttributes
    from ..models.user_key_type_0 import UserKeyType0


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        key (Union['UserKeyType0', str]):
        first_name (str):
        last_name (str):
        email (str):
        phone (Union[Any, str]):
        field_id (Union[Any, Unset, str]): MongoDB document ObjectID
        key_id (Union[Any, Unset, str]):
        attributes (Union[Unset, UserAttributes]):
    """

    key: Union["UserKeyType0", str]
    first_name: str
    last_name: str
    email: str
    phone: Union[Any, str]
    field_id: Union[Any, Unset, str] = UNSET
    key_id: Union[Any, Unset, str] = UNSET
    attributes: Union[Unset, "UserAttributes"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.user_key_type_0 import UserKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, UserKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        first_name = self.first_name
        last_name = self.last_name
        email = self.email
        phone: Union[Any, str]

        phone = self.phone

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

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if key_id is not UNSET:
            field_dict["key_id"] = key_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_attributes import UserAttributes
        from ..models.user_key_type_0 import UserKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["UserKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = UserKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UserKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        email = d.pop("email")

        def _parse_phone(data: object) -> Union[Any, str]:
            return cast(Union[Any, str], data)

        phone = _parse_phone(d.pop("phone"))

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
        attributes: Union[Unset, UserAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = UserAttributes.from_dict(_attributes)

        user = cls(
            key=key,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            field_id=field_id,
            key_id=key_id,
            attributes=attributes,
        )

        user.additional_properties = d
        return user

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
