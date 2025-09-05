import pytest
from environment.asset_management.client import AssetManagementClient
from environment.asset_management.models import Asset


@pytest.fixture
def client():
    return AssetManagementClient()


@pytest.mark.asyncio
async def test_get_assets(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/asset-management/id/asset.json",
        json={
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/asset-management/id/asset/224221",
                    "actualCondition": [
                        {
                            "@id": "http://environment.data.gov.uk/asset-management/def/core/condition/level_2",
                            "prefLabel": "Good",
                        }
                    ],
                    "area": [
                        {
                            "@id": "http://environment.data.gov.uk/registry/def/ea-organization/ea_areas/6-28",
                            "label": "Wessex",
                        },
                        {
                            "@id": "http://environment.data.gov.uk/registry/def/ea-organization/ea_areas/28",
                            "label": "Wessex",
                        },
                    ],
                    "assetStartDate": "2007-06-01",
                    "assetSubType": [
                        {
                            "@id": "http://environment.data.gov.uk/asset-management/id/drl/DebrisScreen",
                            "prefLabel": "Debris Screen",
                        }
                    ],
                    "assetType": {
                        "@id": "http://environment.data.gov.uk/asset-management/id/drl/Structure",
                        "prefLabel": "Structure",
                    },
                    "label": "Not Available",
                    "lastInspectionDate": ["2024-08-09"],
                    "maintenanceTask": [
                        {
                            "@id": "http://environment.data.gov.uk/asset-management/id/maintenance-task/164426-224221",
                            "activitySubType": {
                                "@id": "http://environment.data.gov.uk/asset-management/def/maintenance/activity-type/operational-check",
                            },
                            "activityType": {
                                "@id": "http://environment.data.gov.uk/asset-management/def/maintenance/activity-type/maintain-structures",
                            },
                        }
                    ],
                    "notation": "224221",
                    "primaryPurpose": {
                        "@id": "http://environment.data.gov.uk/asset-management/def/core/purpose/flood-risk-management",
                        "prefLabel": "flood risk management",
                    },
                    "protectionType": {
                        "@id": "http://environment.data.gov.uk/asset-management/def/core/protection-type/fluvial",
                        "label": "fluvial",
                    },
                    "targetCondition": {
                        "@id": "http://environment.data.gov.uk/asset-management/def/core/condition/level_3",
                        "prefLabel": "Fair",
                    },
                    "waterCourseName": "Brislington Brook",
                    "bank": {
                        "@id": "http://environment.data.gov.uk/asset-management/def/core/bank/left"
                    },
                    "assetLength": [100.0, 200.0],
                }
            ]
        },
    )
    assets = await client.get_assets()
    assert isinstance(assets, list)
    assert isinstance(assets[0], Asset)
