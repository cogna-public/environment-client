from pydantic import BaseModel, Field
from typing import List, Optional, Union


class PrefLabel(BaseModel):
    id: str = Field(..., alias="@id")
    prefLabel: str = Field(..., alias="prefLabel")


class Area(BaseModel):
    id: str = Field(..., alias="@id")
    label: str


class AssetSubType(BaseModel):
    id: str = Field(..., alias="@id")
    prefLabel: str


class AssetType(BaseModel):
    id: str = Field(..., alias="@id")
    prefLabel: str


class MaintenanceTask(BaseModel):
    id: str = Field(..., alias="@id")
    activitySubType: dict
    activityType: dict


class PrimaryPurpose(BaseModel):
    id: str = Field(..., alias="@id")
    prefLabel: str


class ProtectionType(BaseModel):
    id: str = Field(..., alias="@id")
    label: str


class TargetCondition(BaseModel):
    id: str = Field(..., alias="@id")
    prefLabel: str


class Asset(BaseModel):
    id: str = Field(..., alias="@id")
    actualCondition: Optional[Union[PrefLabel, List[PrefLabel]]] = None
    area: Union[List[Area], Area]
    assetStartDate: Optional[str] = None
    assetSubType: Union[AssetSubType, List[AssetSubType]]
    assetType: AssetType
    label: str
    lastInspectionDate: Optional[Union[str, List[str]]] = None
    maintenanceTask: Optional[List[MaintenanceTask]] = None
    notation: str
    primaryPurpose: PrimaryPurpose
    protectionType: ProtectionType
    targetCondition: Optional[PrefLabel] = None
    waterCourseName: Optional[str] = None
    actualDcl: Optional[float] = None
    actualUcl: Optional[float] = None
    assetLength: Optional[Union[float, List[float]]] = None
    bank: Optional[dict] = None
    designDcl: Optional[float] = None
    designUcl: Optional[float] = None
    currentSop: Optional[float] = None
    # Additional fields based on common API patterns and documentation summary
    description: Optional[str] = None
    status: Optional[str] = None
    location: Optional[dict] = None  # Assuming location might be a nested object


class MaintenanceActivity(BaseModel):
    id: str = Field(..., alias="@id")
    label: Optional[str] = None
    description: Optional[str] = None
    activityType: Optional[dict] = None  # Assuming a nested object for activity type
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class MaintenancePlan(BaseModel):
    id: str = Field(..., alias="@id")
    label: Optional[str] = None
    description: Optional[str] = None
    planType: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class CapitalScheme(BaseModel):
    id: str = Field(..., alias="@id")
    label: Optional[str] = None
    description: Optional[str] = None
    schemeType: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
