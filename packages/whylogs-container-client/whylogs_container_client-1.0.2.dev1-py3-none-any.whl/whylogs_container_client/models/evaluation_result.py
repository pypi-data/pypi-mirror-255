from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.evaluation_result_metrics_item import EvaluationResultMetricsItem
    from ..models.validation_result import ValidationResult


T = TypeVar("T", bound="EvaluationResult")


@_attrs_define
class EvaluationResult:
    """
    Attributes:
        metrics (List['EvaluationResultMetricsItem']):
        validation_results (ValidationResult):
    """

    metrics: List["EvaluationResultMetricsItem"]
    validation_results: "ValidationResult"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        validation_results = self.validation_results.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metrics": metrics,
                "validation_results": validation_results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.evaluation_result_metrics_item import EvaluationResultMetricsItem
        from ..models.validation_result import ValidationResult

        d = src_dict.copy()
        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = EvaluationResultMetricsItem.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        validation_results = ValidationResult.from_dict(d.pop("validation_results"))

        evaluation_result = cls(
            metrics=metrics,
            validation_results=validation_results,
        )

        evaluation_result.additional_properties = d
        return evaluation_result

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
