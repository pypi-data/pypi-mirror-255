from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.delete_site_key_type_0 import DeleteSiteKeyType0


T = TypeVar("T", bound="DeleteSite")


@_attrs_define
class DeleteSite:
    """
    Attributes:
        key (Union['DeleteSiteKeyType0', str]):
    """

    key: Union["DeleteSiteKeyType0", str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.delete_site_key_type_0 import DeleteSiteKeyType0

        key: Union[Dict[str, Any], str]

        if isinstance(self.key, DeleteSiteKeyType0):
            key = self.key.to_dict()

        else:
            key = self.key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.delete_site_key_type_0 import DeleteSiteKeyType0

        d = src_dict.copy()

        def _parse_key(data: object) -> Union["DeleteSiteKeyType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = DeleteSiteKeyType0.from_dict(data)

                return key_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DeleteSiteKeyType0", str], data)

        key = _parse_key(d.pop("key"))

        delete_site = cls(
            key=key,
        )

        delete_site.additional_properties = d
        return delete_site

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
