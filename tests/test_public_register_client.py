import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import httpx

from environment.public_register import PublicRegisterClient
from environment.public_register.models import (
    RegistrationSearchResponse,
    RegistrationSummary,
    RegistrationDetail,
    Metadata,
)


class TestPublicRegisterClient:
    """Test cases for the PublicRegisterClient."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a PublicRegisterClient instance for testing."""
        async with PublicRegisterClient() as client:
            yield client

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that the client initializes correctly."""
        client = PublicRegisterClient()
        assert str(client.base_url) == "https://environment.data.gov.uk/public-register/"
        await client.aclose()

    @pytest.mark.asyncio
    async def test_client_with_custom_timeout(self):
        """Test that the client accepts custom timeout."""
        client = PublicRegisterClient(timeout=60.0)
        assert str(client.base_url) == "https://environment.data.gov.uk/public-register/"
        await client.aclose()

    @pytest.mark.asyncio
    async def test_search_all_registers(self, client):
        """Test searching across all registers."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 10,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/waste-operations/registration/CB/HE5831CE",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/waste-operations",
                        "label": "Waste Operations",
                    },
                    "registrationNumber": "CB/HE5831CE",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/12345",
                        "name": "Test Company Limited",
                        "tradingName": "Test Co",
                    },
                    "expiryDate": "2025-12-31",
                    "registrationDate": "2020-01-01",
                    "site": {
                        "@id": "http://environment.data.gov.uk/public-register/site/67890",
                        "siteAddress": {
                            "address": "123 Test Street, Test Town, TE1 1ST",
                            "postcode": "TE1 1ST",
                        },
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.search_all_registers(name_search="Test", limit=10)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "CB/HE5831CE"
            assert result.items[0].holder.name == "Test Company Limited"

            mock_get.assert_called_once_with(
                "/api/search.json",
                params={"name-search": "Test", "_limit": 10},
            )

    @pytest.mark.asyncio
    async def test_get_completion(self, client):
        """Test getting completion suggestions."""
        mock_completion_data = ["Test Company Limited", "Test Holdings Ltd", "Test Industries"]

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_completion_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_completion("Test")

            assert result == mock_completion_data
            mock_get.assert_called_once_with(
                "/api/completion.json",
                params={"q": "Test", "_limit": None},
            )

    @pytest.mark.asyncio
    async def test_get_waste_operations(self, client):
        """Test getting waste operations registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/waste-operations/registration/CB/HE5831CE",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/waste-operations",
                        "label": "Waste Operations",
                    },
                    "registrationNumber": "CB/HE5831CE",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/12345",
                        "name": "Waste Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_waste_operations(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "CB/HE5831CE"

            mock_get.assert_called_once_with(
                "/waste-operations/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_waste_operation_by_id(self, client):
        """Test getting a specific waste operation by ID."""
        mock_response_data = {
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/waste-operations/registration/CB/HE5831CE",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/waste-operations",
                        "label": "Waste Operations",
                    },
                    "registrationNumber": "CB/HE5831CE",
                    "type": [
                        {
                            "@id": "http://environment.data.gov.uk/public-register/vocab/Registration",
                        }
                    ],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/12345",
                        "name": "Waste Company Limited",
                        "tradingName": "Waste Co",
                    },
                    "label": "Waste Operations Registration CB/HE5831CE",
                    "notation": ["CB/HE5831CE"],
                    "expiryDate": "2025-12-31",
                    "registrationDate": "2020-01-01",
                    "site": {
                        "@id": "http://environment.data.gov.uk/public-register/site/67890",
                        "siteAddress": {
                            "address": "123 Waste Street, Waste Town, WE1 1ST",
                            "postcode": "WE1 1ST",
                        },
                        "location": {
                            "easting": 500000.0,
                            "northing": 200000.0,
                            "gridReference": "TQ123456",
                        },
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_waste_operation_by_id("CB/HE5831CE")

            assert isinstance(result, RegistrationDetail)
            assert result.registration_number == "CB/HE5831CE"
            assert result.holder.name == "Waste Company Limited"

            mock_get.assert_called_once_with(
                "/waste-operations/registration/CB/HE5831CE.json",
            )

    @pytest.mark.asyncio
    async def test_get_end_of_life_vehicles(self, client):
        """Test getting end of life vehicle registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/end-of-life-vehicles/registration/ELV123",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/end-of-life-vehicles",
                        "label": "End of Life Vehicles",
                    },
                    "registrationNumber": "ELV123",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/54321",
                        "name": "Vehicle Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_end_of_life_vehicles(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "ELV123"

            mock_get.assert_called_once_with(
                "/end-of-life-vehicles/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_industrial_installations(self, client):
        """Test getting industrial installation registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/industrial-installations/registration/II456",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/industrial-installations",
                        "label": "Industrial Installations",
                    },
                    "registrationNumber": "II456",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/98765",
                        "name": "Industrial Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_industrial_installations(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "II456"

            mock_get.assert_called_once_with(
                "/industrial-installations/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_water_discharges(self, client):
        """Test getting water discharge registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/water-discharges/registration/WD789",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/water-discharges",
                        "label": "Water Discharges",
                    },
                    "registrationNumber": "WD789",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/11111",
                        "name": "Water Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_water_discharges(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "WD789"

            mock_get.assert_called_once_with(
                "/water-discharges/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_radioactive_substances(self, client):
        """Test getting radioactive substance registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/radioactive-substance/registration/RS012",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/radioactive-substance",
                        "label": "Radioactive Substances",
                    },
                    "registrationNumber": "RS012",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/22222",
                        "name": "Radioactive Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_radioactive_substances(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "RS012"

            mock_get.assert_called_once_with(
                "/radioactive-substance/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_waste_carriers_brokers(self, client):
        """Test getting waste carriers and brokers registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/waste-carriers-brokers/registration/WCB345",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/waste-carriers-brokers",
                        "label": "Waste Carriers and Brokers",
                    },
                    "registrationNumber": "WCB345",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/33333",
                        "name": "Carrier Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_waste_carriers_brokers(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "WCB345"

            mock_get.assert_called_once_with(
                "/waste-carriers-brokers/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_waste_exemptions(self, client):
        """Test getting waste exemption registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/waste-exemptions/registration/WEX678",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/waste-exemptions",
                        "label": "Waste Exemptions",
                    },
                    "registrationNumber": "WEX678",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/44444",
                        "name": "Exemption Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_waste_exemptions(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "WEX678"

            mock_get.assert_called_once_with(
                "/waste-exemptions/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_water_discharge_exemptions(self, client):
        """Test getting water discharge exemption registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/water-discharge-exemptions/registration/WDE901",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/water-discharge-exemptions",
                        "label": "Water Discharge Exemptions",
                    },
                    "registrationNumber": "WDE901",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/55555",
                        "name": "Water Exemption Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_water_discharge_exemptions(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "WDE901"

            mock_get.assert_called_once_with(
                "/water-discharge-exemptions/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_scrap_metal_dealers(self, client):
        """Test getting scrap metal dealer registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/scrap-metal-dealers/registration/SMD234",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/scrap-metal-dealers",
                        "label": "Scrap Metal Dealers",
                    },
                    "registrationNumber": "SMD234",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/66666",
                        "name": "Scrap Metal Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_scrap_metal_dealers(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "SMD234"

            mock_get.assert_called_once_with(
                "/scrap-metal-dealers/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_enforcement_actions(self, client):
        """Test getting enforcement action registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/enforcement-action/registration/EA567",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/enforcement-action",
                        "label": "Enforcement Actions",
                    },
                    "registrationNumber": "EA567",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/77777",
                        "name": "Enforcement Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_enforcement_actions(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "EA567"

            mock_get.assert_called_once_with(
                "/enforcement-action/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_get_flood_risk_exemptions(self, client):
        """Test getting flood risk exemption registrations."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/flood-risk-exemptions/registration/FRE890",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/flood-risk-exemptions",
                        "label": "Flood Risk Exemptions",
                    },
                    "registrationNumber": "FRE890",
                    "type": ["http://environment.data.gov.uk/public-register/vocab/Registration"],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/88888",
                        "name": "Flood Risk Company Limited",
                    },
                }
            ],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_flood_risk_exemptions(limit=5)

            assert isinstance(result, RegistrationSearchResponse)
            assert len(result.items) == 1
            assert result.items[0].registration_number == "FRE890"

            mock_get.assert_called_once_with(
                "/flood-risk-exemptions/registration.json",
                params={"_limit": 5},
            )

    @pytest.mark.asyncio
    async def test_download_waste_operations(self, client):
        """Test downloading waste operations data."""
        mock_csv_data = b"Registration Number,Holder Name,Address\nCB/HE5831CE,Test Company,123 Test Street"

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.content = mock_csv_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.download_waste_operations()

            assert result == mock_csv_data
            mock_get.assert_called_once_with(
                "/downloads/waste-operations",
                params={},
            )

    @pytest.mark.asyncio
    async def test_search_with_location_parameters(self, client):
        """Test searching with location-based parameters."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 10,
                "offset": 0,
            },
            "items": [],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.search_all_registers(
                easting=500000.0,
                northing=200000.0,
                dist=10.0,
                local_authority="Test Authority",
            )

            assert isinstance(result, RegistrationSearchResponse)
            mock_get.assert_called_once_with(
                "/api/search.json",
                params={
                    "easting": 500000.0,
                    "northing": 200000.0,
                    "dist": 10.0,
                    "local-authority": "Test Authority",
                },
            )

    @pytest.mark.asyncio
    async def test_search_with_name_number_search(self, client):
        """Test searching with name-number-search parameter."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 10,
                "offset": 0,
            },
            "items": [],
        }

        with patch.object(client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.search_all_registers(
                name_number_search="Test",
                limit=10,
            )

            assert isinstance(result, RegistrationSearchResponse)
            mock_get.assert_called_once_with(
                "/api/search.json",
                params={
                    "name-number-search": "Test",
                    "_limit": 10,
                },
            )

    @pytest.mark.asyncio
    async def test_verbose_logging(self):
        """Test that verbose logging works correctly."""
        client = PublicRegisterClient(verbose=True)
        
        # Check that event hooks are set up
        assert len(client.event_hooks["request"]) == 1
        assert len(client.event_hooks["response"]) == 1
        
        await client.aclose()
