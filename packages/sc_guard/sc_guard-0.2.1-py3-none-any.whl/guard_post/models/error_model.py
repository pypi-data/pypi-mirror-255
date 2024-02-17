from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET

if TYPE_CHECKING:
    from ..models.error_model_details_type_0_item import ErrorModelDetailsType0Item


T = TypeVar("T", bound="ErrorModel")


@_attrs_define
class ErrorModel:
    """Define base error model for the response.

    Attributes:
        code (int): HTTP error status code.
        message (str): Detail on HTTP error.
        status (str): HTTP error reason-phrase as per in RFC7235. NOTE! Set
            automatically based on HTTP error status code.

    Raises:
        pydantic.error_wrappers.ValidationError: If any of provided attribute
            doesn't pass type validation.

        Attributes:
            code (int):
            message (str):
            details (Union[Any, List['ErrorModelDetailsType0Item']]):
    """

    code: int
    message: str
    details: Union[Any, List["ErrorModelDetailsType0Item"]]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code = self.code
        message = self.message
        details: Union[Any, List[Dict[str, Any]]]

        if isinstance(self.details, list):
            details = []
            for details_type_0_item_data in self.details:
                details_type_0_item = details_type_0_item_data.to_dict()

                details.append(details_type_0_item)

        else:
            details = self.details

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "message": message,
                "details": details,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.error_model_details_type_0_item import ErrorModelDetailsType0Item

        d = src_dict.copy()
        code = d.pop("code")

        message = d.pop("message")

        def _parse_details(
            data: object,
        ) -> Union[Any, List["ErrorModelDetailsType0Item"]]:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                details_type_0 = UNSET
                _details_type_0 = data
                for details_type_0_item_data in _details_type_0:
                    details_type_0_item = ErrorModelDetailsType0Item.from_dict(
                        details_type_0_item_data
                    )

                    details_type_0.append(details_type_0_item)

                return details_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Any, List["ErrorModelDetailsType0Item"]], data)

        details = _parse_details(d.pop("details"))

        error_model = cls(
            code=code,
            message=message,
            details=details,
        )

        error_model.additional_properties = d
        return error_model

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
