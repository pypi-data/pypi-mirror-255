"""Models for WireGuard status API."""
from dataclasses import dataclass
from datetime import UTC, datetime

from .const import ENDPOINT, LATEST_HANDSHAKE, NONE_ENDPOINT, TRANSFER_RX, TRANSFER_TX
from .exceptions import WireGuardInvalidJson


@dataclass(frozen=True)
class WireGuardPeer:
    """Data representation of a WireGuard peer."""

    name: str
    endpoint: str | None
    latest_handshake: datetime | None
    transfer_rx: int
    transfer_tx: int

    @staticmethod
    def from_data(name: str, data: dict[str, str | int]) -> "WireGuardPeer":
        """Create a WireGuardPeer from a dictionary."""
        if any(
            k not in data
            for k in (ENDPOINT, LATEST_HANDSHAKE, TRANSFER_RX, TRANSFER_TX)
        ):
            raise WireGuardInvalidJson("Invalid JSON", {"data": data})
        return WireGuardPeer(
            name=name,
            endpoint=data[ENDPOINT] if data[ENDPOINT] != NONE_ENDPOINT else None,
            latest_handshake=datetime.fromtimestamp(data[LATEST_HANDSHAKE], UTC)
            if data[LATEST_HANDSHAKE] > 0
            else None,
            transfer_rx=data[TRANSFER_RX],
            transfer_tx=data[TRANSFER_TX],
        )
