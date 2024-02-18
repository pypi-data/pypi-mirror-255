from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.process_logger_status_response_statuses import ProcessLoggerStatusResponseStatuses


T = TypeVar("T", bound="ProcessLoggerStatusResponse")


@_attrs_define
class ProcessLoggerStatusResponse:
    """
    Attributes:
        version (str):
        statuses (ProcessLoggerStatusResponseStatuses):
    """

    version: str
    statuses: "ProcessLoggerStatusResponseStatuses"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        version = self.version

        statuses = self.statuses.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "statuses": statuses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.process_logger_status_response_statuses import ProcessLoggerStatusResponseStatuses

        d = src_dict.copy()
        version = d.pop("version")

        statuses = ProcessLoggerStatusResponseStatuses.from_dict(d.pop("statuses"))

        process_logger_status_response = cls(
            version=version,
            statuses=statuses,
        )

        process_logger_status_response.additional_properties = d
        return process_logger_status_response

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
