from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AppPortalAccessIn")


@attr.s(auto_attribs=True)
class AppPortalAccessIn:
    """
    Attributes:
        feature_flags (Union[Unset, List[str]]): The set of feature flags the created token will have access to.
    """

    feature_flags: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        feature_flags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.feature_flags, Unset):
            feature_flags = self.feature_flags

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if feature_flags is not UNSET:
            field_dict["featureFlags"] = feature_flags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        feature_flags = cast(List[str], d.pop("featureFlags", UNSET))

        app_portal_access_in = cls(
            feature_flags=feature_flags,
        )

        app_portal_access_in.additional_properties = d
        return app_portal_access_in

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
