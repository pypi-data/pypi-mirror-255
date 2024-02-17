from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_user_attributes import CreateUserAttributes
    from ..models.create_user_key_type_0 import CreateUserKeyType0


T = TypeVar("T", bound="CreateUser")


@_attrs_define
class CreateUser:
    """
    Attributes:
        key (Union['CreateUserKeyType0', str]):
        first_name (str):
        last_name (str):
        email (str):
        phone (Union[Any, str]):
        attributes (CreateUserAttributes):
    """

    key: Union["CreateUserKeyType0", str]
    first_name: str
    last_name: str
    email: str
    phone: Union[Any, str]
    attributes: "CreateUserAttributes"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_user_key_type_0 import CreateUserKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, CreateUserKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        first_name = self.first_name
        last_name = self.last_name
        email = self.email
        phone: Union[Any, str]

        phone = self.phone

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
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_user_attributes import CreateUserAttributes
        from ..models.create_user_key_type_0 import CreateUserKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["CreateUserKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = CreateUserKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CreateUserKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        email = d.pop("email")

        def _parse_phone(data: object) -> Union[Any, str]:
            return cast(Union[Any, str], data)

        phone = _parse_phone(d.pop("phone"))

        attributes = CreateUserAttributes.from_dict(d.pop("attributes"))

        create_user = cls(
            key=key,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            attributes=attributes,
        )

        create_user.additional_properties = d
        return create_user

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
