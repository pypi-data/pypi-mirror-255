"""Tests for model.py."""
from dataclasses import FrozenInstanceError
from datetime import datetime

from ha_wireguard_api.exceptions import WireGuardInvalidJson
from ha_wireguard_api.model import WireGuardPeer
import pytest

from tests import load_fixture


def test_peer() -> None:
    """Test WireGuardPeer."""
    peer = WireGuardPeer(
        name="Dummy",
        endpoint="localhost:1234",
        latest_handshake=datetime(2022, 1, 1),
        transfer_rx=1234,
        transfer_tx=4321,
    )
    assert peer.name == "Dummy"
    assert peer.endpoint == "localhost:1234"
    assert peer.latest_handshake == datetime(2022, 1, 1)
    assert peer.transfer_rx == 1234
    assert peer.transfer_tx == 4321


def test_peer_frozen(peer: WireGuardPeer) -> None:
    """Test WireGuardPeer is frozen."""
    assert peer.name == "Dummy"
    assert peer.endpoint == "localhost:1234"
    assert peer.latest_handshake == datetime(2022, 1, 1)
    assert peer.transfer_rx == 1234
    assert peer.transfer_tx == 4321

    with pytest.raises(FrozenInstanceError):
        peer.name = "Spam"
    with pytest.raises(FrozenInstanceError):
        peer.endpoint = "spam:1234"
    with pytest.raises(FrozenInstanceError):
        peer.latest_handshake = datetime(2022, 1, 2)
    with pytest.raises(FrozenInstanceError):
        peer.transfer_rx = 5678
    with pytest.raises(FrozenInstanceError):
        peer.transfer_tx = 8765

    assert peer.name == "Dummy"
    assert peer.endpoint == "localhost:1234"
    assert peer.latest_handshake == datetime(2022, 1, 1)
    assert peer.transfer_rx == 1234
    assert peer.transfer_tx == 4321


def test_peer_from_data() -> None:
    """Test creation of WireGuardPeer from data."""
    json = load_fixture("data.json")
    name, data = json.popitem()

    peer = WireGuardPeer.from_data(name, data)
    assert peer.name == "Dummy"
    assert peer.endpoint is None
    assert peer.latest_handshake is None
    assert peer.transfer_rx == 0
    assert peer.transfer_tx == 0


def test_peer_from_invalid_data() -> None:
    """Test creation of WireGuardPeer with invalid data."""
    json = load_fixture("invalid.json")
    name, data = json.popitem()

    with pytest.raises(WireGuardInvalidJson):
        WireGuardPeer.from_data(name, data)
