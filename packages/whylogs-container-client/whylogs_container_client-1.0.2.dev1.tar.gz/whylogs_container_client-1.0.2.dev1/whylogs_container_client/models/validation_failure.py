from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ValidationFailure")


@_attrs_define
class ValidationFailure:
    """
    Attributes:
        id (int):
        metric (str):
        details (str):
        value (Union[None, float, int, str]):
        upper_threshold (Union[None, Unset, float]):
        lower_threshold (Union[None, Unset, float]):
    """

    id: int
    metric: str
    details: str
    value: Union[None, float, int, str]
    upper_threshold: Union[None, Unset, float] = UNSET
    lower_threshold: Union[None, Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        metric = self.metric

        details = self.details

        value: Union[None, float, int, str]
        value = self.value

        upper_threshold: Union[None, Unset, float]
        if isinstance(self.upper_threshold, Unset):
            upper_threshold = UNSET
        else:
            upper_threshold = self.upper_threshold

        lower_threshold: Union[None, Unset, float]
        if isinstance(self.lower_threshold, Unset):
            lower_threshold = UNSET
        else:
            lower_threshold = self.lower_threshold

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "metric": metric,
                "details": details,
                "value": value,
            }
        )
        if upper_threshold is not UNSET:
            field_dict["upper_threshold"] = upper_threshold
        if lower_threshold is not UNSET:
            field_dict["lower_threshold"] = lower_threshold

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        metric = d.pop("metric")

        details = d.pop("details")

        def _parse_value(data: object) -> Union[None, float, int, str]:
            if data is None:
                return data
            return cast(Union[None, float, int, str], data)

        value = _parse_value(d.pop("value"))

        def _parse_upper_threshold(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        upper_threshold = _parse_upper_threshold(d.pop("upper_threshold", UNSET))

        def _parse_lower_threshold(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        lower_threshold = _parse_lower_threshold(d.pop("lower_threshold", UNSET))

        validation_failure = cls(
            id=id,
            metric=metric,
            details=details,
            value=value,
            upper_threshold=upper_threshold,
            lower_threshold=lower_threshold,
        )

        validation_failure.additional_properties = d
        return validation_failure

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
