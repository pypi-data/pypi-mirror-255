from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LLMValidateRequest")


@_attrs_define
class LLMValidateRequest:
    """
    Attributes:
        dataset_id (str):
        prompt (Union[None, Unset, str]):
        response (Union[None, Unset, str]):
        timestamp (Union[None, Unset, int]):
    """

    dataset_id: str
    prompt: Union[None, Unset, str] = UNSET
    response: Union[None, Unset, str] = UNSET
    timestamp: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_id = self.dataset_id

        prompt: Union[None, Unset, str]
        if isinstance(self.prompt, Unset):
            prompt = UNSET
        else:
            prompt = self.prompt

        response: Union[None, Unset, str]
        if isinstance(self.response, Unset):
            response = UNSET
        else:
            response = self.response

        timestamp: Union[None, Unset, int]
        if isinstance(self.timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = self.timestamp

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasetId": dataset_id,
            }
        )
        if prompt is not UNSET:
            field_dict["prompt"] = prompt
        if response is not UNSET:
            field_dict["response"] = response
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_id = d.pop("datasetId")

        def _parse_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        prompt = _parse_prompt(d.pop("prompt", UNSET))

        def _parse_response(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        response = _parse_response(d.pop("response", UNSET))

        def _parse_timestamp(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        timestamp = _parse_timestamp(d.pop("timestamp", UNSET))

        llm_validate_request = cls(
            dataset_id=dataset_id,
            prompt=prompt,
            response=response,
            timestamp=timestamp,
        )

        llm_validate_request.additional_properties = d
        return llm_validate_request

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
