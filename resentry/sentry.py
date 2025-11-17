from __future__ import annotations

import io
import json
import gzip
import typing
from typing import TypedDict

from resentry.utils.helpers import (
    async_json_loads,
    async_decode_utf8,
    async_gzip_decompress,
    async_brotli_decompress,
)


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
        self.payload_json = self.get_payload_json()

    def get_payload_bytes(self) -> bytes:
        """Returns the raw payload bytes."""
        return self.payload

    def get_payload_json(self) -> dict[str, typing.Any] | None:
        """Returns the payload as JSON if it's JSON-compatible."""
        if self.content_type.startswith("application/json"):
            try:
                data = self.payload.decode("utf-8", "replace")
                return json.loads(data)
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


async def parse_json_async(
    data: bytes,
) -> typing.Any:  # Using Any since JSON parsing results can be different types
    """
    Safely parse JSON from bytes, handling UTF-8 encoding asynchronously.
    """
    if isinstance(data, bytes):
        data_str = await async_decode_utf8(data)
        return await async_json_loads(data_str)
    else:
        return await async_json_loads(data)


def parse_json(
    data: bytes,
) -> typing.Any:  # Using Any since JSON parsing results can be different types
    """
    Safely parse JSON from bytes, handling UTF-8 encoding.
    """
    if isinstance(data, bytes):
        data_str = data.decode("utf-8", "replace")
    else:
        data_str = data
    return json.loads(data_str)


async def unpack_sentry_envelope_async(envelope_data: bytes) -> Envelope:
    """
    Unpacks a Sentry envelope from raw bytes asynchronously.

    Args:
        envelope_data: Raw bytes of the envelope (may be compressed)

    Returns:
        Deserialized Envelope object
    """
    # First, check for compression and decompress if necessary
    if envelope_data.startswith(b"\x1f\x8b"):  # Gzip magic number
        envelope_data = await async_gzip_decompress(envelope_data)
    elif envelope_data.startswith(b"\x42\x5a"):  # Brotli magic number (partial check)
        try:
            envelope_data = await async_brotli_decompress(envelope_data)
        except ImportError:
            raise ValueError(
                "Brotli compression detected but brotli module not available",
            )

    # Create a file-like object for reading the envelope
    buffer = io.BytesIO(envelope_data)

    # Read the envelope headers (first line)
    header_line = buffer.readline().rstrip(b"\n")
    envelope_headers = (
        parse_json(header_line) if header_line else {}
    )  # Using sync version for in-memory operations

    # Parse items until we run out of data
    items = []
    while True:
        # Read item header
        item_header_line = buffer.readline().rstrip(b"\n")
        if not item_header_line:
            break

        try:
            item_headers = parse_json(
                item_header_line
            )  # Using sync version for in-memory operations
        except json.JSONDecodeError:
            # If we can't parse the header, we've likely reached the end or have malformed data
            break

        # Get the length of the payload
        length = item_headers.get("length", 0)
        # Convert length to int if it's a string
        if isinstance(length, str):
            try:
                length = int(length)
            except ValueError:
                length = 0

        # Ensure length is a non-negative integer
        if length is not None and isinstance(length, int) and length >= 0:
            # Read exactly `length` bytes for the payload
            payload = buffer.read(length)
            # Read and discard the trailing newline
            buffer.readline()
        else:
            # If no length specified, read up to the next newline
            payload = buffer.readline().rstrip(b"\n")

        # Ensure payload is bytes
        if isinstance(payload, str):
            payload = payload.encode("utf-8")

        # Create the envelope item - cast headers to proper type
        item = EnvelopeItem(
            headers=typing.cast(ItemHeader, item_headers), payload=payload
        )
        items.append(item)

    return Envelope(headers=typing.cast(EnvelopeHeader, envelope_headers), items=items)


def unpack_sentry_envelope(envelope_data: bytes) -> Envelope:
    """
    Unpacks a Sentry envelope from raw bytes synchronously.

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
    envelope_headers = (
        parse_json(header_line) if header_line else {}
    )  # Using sync version for in-memory operations

    # Parse items until we run out of data
    items = []
    while True:
        # Read item header
        item_header_line = buffer.readline().rstrip(b"\n")
        if not item_header_line:
            break

        try:
            item_headers = parse_json(
                item_header_line
            )  # Using sync version for in-memory operations
        except json.JSONDecodeError:
            # If we can't parse the header, we've likely reached the end or have malformed data
            break

        # Get the length of the payload
        length = item_headers.get("length", 0)
        # Convert length to int if it's a string
        if isinstance(length, str):
            try:
                length = int(length)
            except ValueError:
                length = 0

        # Ensure length is a non-negative integer
        if length is not None and isinstance(length, int) and length >= 0:
            # Read exactly `length` bytes for the payload
            payload = buffer.read(length)
            # Read and discard the trailing newline
            buffer.readline()
        else:
            # If no length specified, read up to the next newline
            payload = buffer.readline().rstrip(b"\n")

        # Ensure payload is bytes
        if isinstance(payload, str):
            payload = payload.encode("utf-8")

        # Create the envelope item - cast headers to proper type
        item = EnvelopeItem(
            headers=typing.cast(ItemHeader, item_headers), payload=payload
        )
        items.append(item)

    return Envelope(headers=typing.cast(EnvelopeHeader, envelope_headers), items=items)


async def unpack_sentry_envelope_from_request_async(
    envelope_bytes: bytes,
    content_encoding: str | None = None,
) -> Envelope:
    """
    Unpack a Sentry envelope from HTTP request data asynchronously.

    Args:
        envelope_bytes: The raw envelope data from the HTTP request body
        content_encoding: The content encoding header (e.g., 'gzip', 'br')

    Returns:
        Deserialized Envelope object
    """
    # Handle compression based on Content-Encoding header
    if content_encoding == "gzip":
        envelope_bytes = await async_gzip_decompress(envelope_bytes)
    elif content_encoding == "br":
        try:
            envelope_bytes = await async_brotli_decompress(envelope_bytes)
        except ImportError:
            raise ValueError(
                "Brotli compression detected but brotli module not available",
            )

    return await unpack_sentry_envelope_async(envelope_bytes)


def unpack_sentry_envelope_from_request(
    envelope_bytes: bytes,
    content_encoding: str | None = None,
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
