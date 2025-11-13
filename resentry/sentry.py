from __future__ import annotations

import io
import json
import gzip
import typing
from typing import TypedDict


class EnvelopeHeader(TypedDict, total=False):
    """Represents the envelope headers."""

    event_id: str | None
    sent_at: str | None
    dsn: str | None


class ItemHeader(TypedDict, total=False):
    """Represents an item header within the envelope."""

    type: str
    length: int
    content_type: str
    filename: str | None


class EnvelopeItem:
    """Represents a single item within the envelope."""

    def __init__(self, headers: ItemHeader, payload: bytes):
        self.headers = headers
        self.payload = payload
        self.type = headers.get("type", "unknown")
        self.content_type = headers.get("content_type", "application/octet-stream")
        self.length = headers.get("length", len(payload))

    def get_payload_bytes(self) -> bytes:
        """Returns the raw payload bytes."""
        return self.payload

    def get_payload_json(self) -> dict[str, typing.Any] | None:
        """Returns the payload as JSON if it's JSON-compatible."""
        if self.content_type.startswith("application/json"):
            try:
                return json.loads(self.payload.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        return None

    def __repr__(self) -> str:
        return f"<EnvelopeItem type={self.type} content_type={self.content_type} length={len(self.payload)}>"


class Envelope:
    """Represents a Sentry envelope received on the server side."""

    def __init__(self, headers: EnvelopeHeader, items: list[EnvelopeItem]):
        self.headers = headers
        self.items = items

    @property
    def event_id(self) -> str | None:
        """Returns the event ID from envelope headers if present."""
        return self.headers.get("event_id")

    @property
    def description(self) -> str:
        """Provides a description of the envelope."""
        types = [item.type for item in self.items]
        return f"envelope with {len(self.items)} items ({', '.join(types)})"

    def get_event_item(self) -> EnvelopeItem | None:
        """Finds and returns the first event item in the envelope, if any."""
        for item in self.items:
            if item.type == "event":
                return item
        return None

    def get_transaction_item(self) -> EnvelopeItem | None:
        """Finds and returns the first transaction item in the envelope, if any."""
        for item in self.items:
            if item.type == "transaction":
                return item
        return None

    def __repr__(self) -> str:
        return f"<Envelope headers={self.headers} items={len(self.items)}>"


def parse_json(
    data: bytes,
) -> typing.Any:  # Using Any since JSON parsing results can be different types
    """
    Safely parse JSON from bytes, handling UTF-8 encoding.
    """
    if isinstance(data, bytes):
        data = data.decode("utf-8", "replace")
    return json.loads(data)


def unpack_sentry_envelope(envelope_data: bytes) -> Envelope:
    """
    Unpacks a Sentry envelope from raw bytes.

    Args:
        envelope_data: Raw bytes of the envelope (may be compressed)

    Returns:
        Deserialized Envelope object
    """
    # First, check for compression and decompress if necessary
    if envelope_data.startswith(b"\x1f\x8b"):  # Gzip magic number
        envelope_data = gzip.decompress(envelope_data)
    elif envelope_data.startswith(b"\x42\x5a"):  # Brotli magic number (partial check)
        try:
            import brotli  # type: ignore

            envelope_data = brotli.decompress(envelope_data)
        except ImportError:
            raise ValueError(
                "Brotli compression detected but brotli module not available",
            )

    # Create a file-like object for reading the envelope
    buffer = io.BytesIO(envelope_data)

    # Read the envelope headers (first line)
    header_line = buffer.readline().rstrip(b"\n")
    envelope_headers = parse_json(header_line) if header_line else {}

    # Parse items until we run out of data
    items = []
    while True:
        # Read item header
        item_header_line = buffer.readline().rstrip(b"\n")
        if not item_header_line:
            break

        try:
            item_headers = parse_json(item_header_line)
        except json.JSONDecodeError:
            # If we can't parse the header, we've likely reached the end or have malformed data
            break

        # Get the length of the payload
        length = item_headers.get("length", 0)

        if length is not None:
            # Read exactly `length` bytes for the payload
            payload = buffer.read(length)
            # Read and discard the trailing newline
            buffer.readline()
        else:
            # If no length specified, read up to the next newline
            payload = buffer.readline().rstrip(b"\n")

        # Create the envelope item
        item = EnvelopeItem(headers=item_headers, payload=payload)
        items.append(item)

    return Envelope(headers=envelope_headers, items=items)


def unpack_sentry_envelope_from_request(
    envelope_bytes: bytes, content_encoding: str | None = None,
) -> Envelope:
    """
    Unpack a Sentry envelope from HTTP request data.

    Args:
        envelope_bytes: The raw envelope data from the HTTP request body
        content_encoding: The content encoding header (e.g., 'gzip', 'br')

    Returns:
        Deserialized Envelope object
    """
    # Handle compression based on Content-Encoding header
    if content_encoding == "gzip":
        envelope_bytes = gzip.decompress(envelope_bytes)
    elif content_encoding == "br":
        try:
            import brotli  # type: ignore

            envelope_bytes = brotli.decompress(envelope_bytes)
        except ImportError:
            raise ValueError(
                "Brotli compression detected but brotli module not available",
            )

    return unpack_sentry_envelope(envelope_bytes)
