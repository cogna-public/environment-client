import pytest
from environment.bathing_waters.client import BathingWatersClient
from environment.bathing_waters.models import BathingWater


@pytest.fixture
def client():
    return BathingWatersClient()


@pytest.mark.asyncio
async def test_get_bathing_waters(client, httpx_mock):
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/bwq/profiles/bathing-water.json",
        json={
            "result": {
                "items": [
                    {
                        "_about": "http://environment.data.gov.uk/id/bathing-water/ukc2102-03600",
                        "appointedSewerageUndertaker": {
                            "_about": "http://business.data.gov.uk/id/company/02366703",
                            "name": {
                                "_value": "Northumbrian Water Limited",
                                "_lang": "en",
                            },
                        },
                        "country": {
                            "_about": "http://data.ordnancesurvey.co.uk/id/country/england",
                            "name": {"_value": "England", "_lang": "en"},
                        },
                        "district": [
                            {
                                "_about": "http://data.ordnancesurvey.co.uk/id/7000000000009746",
                                "name": {"_value": "Northumberland", "_lang": "en"},
                            },
                            "http://statistics.data.gov.uk/id/statistical-geography/E06000057",
                        ],
                        "eubwidNotation": "ukc2102-03600",
                        "latestComplianceAssessment": {
                            "_about": "http://environment.data.gov.uk/data/bathing-water-quality/compliance-rBWD/point/03600/year/2024",
                            "complianceClassification": {
                                "_about": "http://environment.data.gov.uk/def/bwq-cc-2015/2",
                                "name": {"_value": "Good", "_lang": "en"},
                            },
                        },
                        "latestRiskPrediction": {
                            "_about": "http://environment.data.gov.uk/data/bathing-water-quality/stp-risk-prediction/point/03600/date/20250905-084047",
                            "expiresAt": {
                                "_value": "2025-09-06T08:29:00",
                                "_datatype": "dateTime",
                            },
                            "riskLevel": {
                                "_about": "http://environment.data.gov.uk/def/bwq-stp/normal",
                                "name": {"_value": "normal", "_lang": "en"},
                            },
                        },
                        "latestSampleAssessment": "http://environment.data.gov.uk/data/bathing-water-quality/in-season/sample/point/03600/date/20250826/time/100100/recordDate/20250826",
                        "name": {"_value": "Spittal", "_lang": "en"},
                        "samplingPoint": {
                            "_about": "http://location.data.gov.uk/so/ef/SamplingPoint/bwsp.eaew/03600",
                            "easting": 400800,
                            "lat": 55.756856682381226,
                            "long": -1.988831300159957,
                            "name": {
                                "_value": "Sampling point at Spittal",
                                "_lang": "en",
                            },
                            "northing": 651500,
                        },
                        "sedimentTypesPresent": "http://environment.data.gov.uk/def/bathing-water/sand-sediment",
                        "waterQualityImpactedByHeavyRain": True,
                        "yearDesignated": "http://reference.data.gov.uk/id/year/1988",
                    }
                ]
            }
        },
    )
    bathing_waters = await client.get_bathing_waters()
    assert isinstance(bathing_waters, list)
    assert isinstance(bathing_waters[0], BathingWater)
