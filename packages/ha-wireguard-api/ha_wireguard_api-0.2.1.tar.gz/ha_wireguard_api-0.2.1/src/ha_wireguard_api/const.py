"""Constants for WireGuard status API."""
from typing import Final

ENDPOINT: Final[str] = "endpoint"
LATEST_HANDSHAKE: Final[str] = "latest_handshake"
TRANSFER_RX: Final[str] = "transfer_rx"
TRANSFER_TX: Final[str] = "transfer_tx"

REQUIRED_STATUS: Final[int] = 200
NONE_ENDPOINT: Final[str] = "(none)"

REQUEST_TIMEOUT: Final[int] = 5
