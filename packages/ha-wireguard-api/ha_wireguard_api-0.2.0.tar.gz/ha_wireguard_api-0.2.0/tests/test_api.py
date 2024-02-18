"""Tests for api.py."""
import aiohttp
from aioresponses import aioresponses
import pytest

from ha_wireguard_api.api import WireguardApiClient
from ha_wireguard_api.const import REQUEST_TIMEOUT
from ha_wireguard_api.exceptions import (
    WireGuardInvalidJson,
    WireGuardResponseError,
    WireGuardTimeoutError,
)
from ha_wireguard_api.model import WireGuardPeer

from tests import load_fixture


async def test_client_init_host() -> None:
    """Test the initializer of the WireguardApiClient."""
    client: WireguardApiClient = WireguardApiClient("localhost")
    assert client.host == "localhost"
    assert client.session is None

    client.host = "remotehost"
    assert client.host == "remotehost"


async def test_client_init_session() -> None:
    """Test provide own session."""
    async with aiohttp.ClientSession() as session:
        client: WireguardApiClient = WireguardApiClient("localhost", session)
    assert client.session is not None
    await client.close()
    assert client.session is None


async def test_client_set_timeout(client: WireguardApiClient) -> None:
    """Test setting the request_timeout."""
    assert client.request_timeout == REQUEST_TIMEOUT
    client.request_timeout = 1
    assert client.request_timeout == 1


async def test_client_contextmanager(responses: aioresponses) -> None:
    """Test WireguardApiClient as context manager."""
    responses.get("localhost")
    async with WireguardApiClient("localhost") as client:
        assert client.host == "localhost"
        await client.get_status()
        assert client.session is not None
    assert client.session is None


async def test_client_timeout(
    client: WireguardApiClient, responses: aioresponses
) -> None:
    """Test WireguardApiClient timeout."""
    responses.get("localhost", timeout=True)
    with pytest.raises(WireGuardTimeoutError) as exc:
        await client.get_status()
        assert "Timeout occurred" in str(exc)


async def test_client_unexpected_status(
    client: WireguardApiClient, responses: aioresponses
) -> None:
    """Test WireguardApiClient unexpected status."""
    responses.get("localhost", status=500)
    with pytest.raises(WireGuardResponseError) as exc:
        await client.get_status()
        assert "Unexpected status" in str(exc)


async def test_client_unexpected_content(
    client: WireguardApiClient, responses: aioresponses
) -> None:
    """Test WireguardApiClient unexpected content."""
    responses.get("localhost", content_type="text/plain")
    with pytest.raises(WireGuardResponseError) as exc:
        await client.get_status()
        assert "Unexpected content" in str(exc)


async def test_client_get_peers(
    client: WireguardApiClient, responses: aioresponses
) -> None:
    """Test WireguardApiClient get_peers."""
    responses.get("localhost", body=load_fixture("data.json"))
    peers = await client.get_peers()
    assert all(isinstance(peer, WireGuardPeer) for peer in peers)


async def test_client_get_invalid_peers(
    client: WireguardApiClient, responses: aioresponses
) -> None:
    """Test WireguardApiClient get_peers."""
    responses.get("localhost", body=load_fixture("invalid.json"))
    with pytest.raises(WireGuardInvalidJson):
        await client.get_peers()
