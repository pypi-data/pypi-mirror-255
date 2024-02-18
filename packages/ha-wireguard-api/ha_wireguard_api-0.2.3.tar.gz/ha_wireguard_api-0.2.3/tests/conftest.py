"""Pytest configuration file containing customizations and fixtures."""
from collections.abc import AsyncGenerator, Generator
from datetime import datetime

import aiohttp
from aioresponses import aioresponses
import pytest
import pytest_socket

from ha_wireguard_api.api import WireguardApiClient
from ha_wireguard_api.model import WireGuardPeer


def pytest_runtest_setup():
    """Disable socket calls during tests to ensure network calls are prevented."""
    pytest_socket.socket_allow_hosts(["127.0.0.1"])
    pytest_socket.disable_socket(allow_unix_socket=True)


@pytest.fixture(name="session")
async def fixture_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """Return a ClientSession."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(name="client")
async def fixture_client(
    session: aiohttp.ClientSession,
) -> AsyncGenerator[WireguardApiClient, None]:
    """Return a Spotify client."""
    async with WireguardApiClient(
        host="localhost",
        session=session,
    ) as wireguard_api_client:
        yield wireguard_api_client


@pytest.fixture(name="responses")
def fixture_responses() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses


@pytest.fixture(name="peer")
def fixture_peer() -> WireGuardPeer:
    """Return a fully populated peer."""
    return WireGuardPeer(
        name="Dummy",
        endpoint="localhost:1234",
        latest_handshake=datetime(2022, 1, 1),
        transfer_rx=1234,
        transfer_tx=4321,
    )
