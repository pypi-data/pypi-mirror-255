"""Utilities for exchanging arbitrary python objects over a websocket."""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from enum import Enum
from io import BytesIO
import json
import re
import socket
from typing import Iterable, List, Tuple, Union

import blosc
from geopandas import GeoDataFrame
from geopandas import read_feather as gpd_read_feather
from pandas import DataFrame
from pandas import read_feather
from shapely import from_wkb
from shapely import Geometry
import simple_websocket

# The blosc library can only compress up to 2 GiB at a time, so we transmit data in chunks of this size.
MAX_BLOSC_COMPRESSION_SIZE = 2147483631
MESSAGE_END_FLAG = b'message_ends'
SERIALISED_SUBSTITUTION_PREFIX = '__SERIALISED__'
# Type alias representing either a websocket server or client.
WebSocketAgent = Union[simple_websocket.Server, simple_websocket.Client]


class SerialisationType(str, Enum):
    """Supported serialisation types and their text representation for use in meta data messages."""

    geometry = "wkb"
    table = "feather"


@dataclass
class SerialisationData:
    """Wraps an object to serialise with its serialisation type."""

    serialisation_type: SerialisationType
    data: object


def validate_websocket_endpoint_url(url: str) -> None:
    """
    Validate a websocket endpoint URL.

    Correct URLs are of the form "ws://localhost:1234/endpoint" or similar.

    Parameters
    ----------
    url : str
        The URL to be validated.

    Raises
    ------
    ValueError
        If the Websocket URL is invalid
    """
    # validate the server_url
    assert url.startswith("ws://")
    split_url = re.split(r':|/', url)
    assert len(split_url) >= 6
    address = split_url[3]
    port = int(split_url[4])

    try:
        socket.gethostbyname(address)
    except socket.gaierror:
        raise ValueError(f"{address} does not appear to be a valid address.")

    if port != 9065 and (port <= 1023 or port > 65353 or port % 1 != 0):
        raise ValueError(f"{port} does not appear to be a valid port.")


def _receive_bytes_from_websocket(ws: WebSocketAgent, timeout: float = 30) -> bytes:
    """
    Receive arbitrary bytes object over a websocket.

    Bytes are assumed to be sent in chunks terminated by MESSAGE_END_FLAG.

    Works for both the Client and Server objects provided by simple_websocket.

    Parameters
    ----------
    ws : WebSocketAgent
        The Websocket Client or Server.
    timeout : float
        If provided, will raise RuntimeError if no message is received within this number of seconds.
        By default, 30 seconds.

    Returns
    -------
    bytes
        The decompressed bytes received via the websocket.

    Raises
    ------
    RuntimeError
        If the connection times out or is closed without a message being received.
    """
    message = b''
    message_chunk = b''
    while message_chunk != MESSAGE_END_FLAG and message_chunk is not None:
        try:
            if message_chunk is not None:
                message += message_chunk
            compressed_message_chunk = ws.receive(timeout)
            if compressed_message_chunk is None:
                message_chunk = None
            else:
                message_chunk = blosc.decompress(compressed_message_chunk)
        except simple_websocket.ws.ConnectionClosed:
            # ensure the input buffer is drained
            if len(ws.input_buffer) > 0:
                message_chunk = blosc.decompress(ws.input_buffer.pop(0))
            else:
                message_chunk = None

    if len(message) == 0:
        raise RuntimeError("Attempted to receive from a websocket, but nothing was sent.")

    return message


def _send_bytes_to_websocket(ws: WebSocketAgent, message: bytes) -> None:
    """
    Send arbitrary bytes object over a websocket.

    Bytes are compressed and then transmitted in MESSAGE_CHUNK_SIZE chunks.

    Works for both the Client and Server objects provided by simple_websocket.

    Parameters
    ----------
    ws : WebSocketAgent
        The Websocket Client or Server.
    message : bytes
        The data to be sent over the websocket.
    """
    for i in range(0, len(message), MAX_BLOSC_COMPRESSION_SIZE):
        ws.send(blosc.compress(message[i:i + MAX_BLOSC_COMPRESSION_SIZE]))
    ws.send(blosc.compress(MESSAGE_END_FLAG))


def _serialise_dataframe(df: Union[DataFrame, GeoDataFrame]) -> bytes:
    """
    Serialise a dataframe using the feather table format.

    Parameters
    ----------
    df : DataFrame
        Input dataframe

    Returns
    -------
    bytes
        Serialised feather table.
    """
    feather_buffer = BytesIO()
    df.to_feather(feather_buffer)
    feather_buffer.seek(0)
    return feather_buffer.getvalue()


def _deserialise_feather_bytes_to_dataframe(data: bytes) -> Union[DataFrame, GeoDataFrame]:
    """
    Convert a binary serialised feather table to pandas dataframe.

    Parameters
    ----------
    data : bytes
        Binary serialised feather table.

    Returns
    -------
    Union[DataFrame, GeoDataFrame]
        Input table converted to a pandas dataframe.

    Raises
    ------
    ValueError
        When bytes can't be interpreted as meaningful dataframe.
    """
    try:
        buffer = BytesIO(data)
        df = gpd_read_feather(buffer)
    except ValueError as e:
        # First attempt to deserialise as a geodataframe. If geo meta is missing, we expect a clear ValueError
        # and we then load as a plain dataframe instead.
        if "Missing geo meta" in e.args[0] or "'geo' metadata" in e.args[0]:
            try:
                df = read_feather(BytesIO(data))
            except ValueError as e:
                raise ValueError("Couldn't deserialise table format") from e
        else:
            raise ValueError("Couldn't deserialise table format") from e
    return df


def _extract_objects_to_serialise(data: object, object_dict: List[SerialisationData] = None) \
        -> Tuple[object, List[SerialisationData]]:
    """
    Iterate through an object, replacing complex objects with a placeholder string.

    This recursively traverses the object if it contains dictionaries or lists/iterables.
    When an object to be serialised is found, we explicitly:
       - Replace it with a magic string: SERIALISED_SUBSTITUTION_PREFIX{X} where X is an increasing numermic index.
       - Store the extracted object in a list, where X (above) is its place in this list. We use the
         SerialisationData type to keep both the object and the serialisation information.

    Parameters
    ----------
    data : object
        Input data object. Can be a single dataframe or primitive or a dictionary-like structure.
    object_dict : List[SerialisationData], optional
        Do not use this parameter! It is used in the recursive calls to store extracted object and related information,
        by default None

    Returns
    -------
    Tuple[object, List[SerialisationData]]
       - A json-friendly copy of the input object with all complex child items replaced with
         SERIALISED_SUBSTITUTION_PREFIX{X} where.
         X refers to the index of object in the objects list.
       - A list of objects from the input data decorated with a transmission friendly serialisation type.
    """
    if object_dict is None:
        object_dict = []

    return_data = data
    if isinstance(data, (GeoDataFrame, DataFrame)):
        object_dict.append(SerialisationData(serialisation_type=SerialisationType.table, data=data))
        return_data = f"{SERIALISED_SUBSTITUTION_PREFIX}{len(object_dict)}"
    elif isinstance(data, Geometry):
        object_dict.append(SerialisationData(serialisation_type=SerialisationType.geometry, data=data))
        return_data = f"{SERIALISED_SUBSTITUTION_PREFIX}{len(object_dict)}"
    elif isinstance(data, dict):
        return_data = data.copy()
        for key in return_data:
            return_data[key] = _extract_objects_to_serialise(return_data[key], object_dict)[0]
    # It's important to handle str before Iterable to avoid infinite recursion!
    elif isinstance(data, str):
        pass
    elif isinstance(data, Iterable):
        return_data = []
        for item in data:
            return_data.append(_extract_objects_to_serialise(item, object_dict)[0])
    return return_data, object_dict


def _insert_deserialised_objects(data: object, object_list: List[object]) -> object:
    """
    Iterate through the object, replacing all special placeholder strings with objects.

    This can be a single object or a nested dictionary like structure.

    Parameters
    ----------
    data : object
        Object potentially containing placeholder strings.
    object_list : List[object]
        The list of objects to inject.

    Returns
    -------
    object
        The original object with placeholder references replaced by objects.
    """
    # Default case is return original object when a primitive type.
    return_data = data

    if isinstance(data, dict):
        return_data = data.copy()
        for key in return_data:
            return_data[key] = _insert_deserialised_objects(return_data[key], object_list)
    # It's important to handle str before Iterable to avoid infinite recursion!
    elif isinstance(data, str):
        if SERIALISED_SUBSTITUTION_PREFIX in data:
            # Use regex to extract the id using the expected placeholder pattern.
            match = re.match(f"{SERIALISED_SUBSTITUTION_PREFIX}(\\w+)", data)
            if match:
                item_index = int(match.group(1)) - 1
                return_data = object_list[item_index]
        # Also handle datetimes. Convert a string to a datetime whenever possible.
        else:
            with suppress(ValueError):
                # fromisoformat is a sensible level of stict, it allows 2001-01-01 but disallows 2001, 20010101
                return_data = datetime.fromisoformat(data)

    elif isinstance(data, Iterable):
        return_data = []
        for item in data:
            return_data.append(_insert_deserialised_objects(item, object_list))
    return return_data


def _date_serialiser(item: object) -> str:
    if isinstance(item, (datetime, date)):
        return item.isoformat()
    else:
        raise TypeError(repr(item) + " is not JSON serializable")


def send_object_to_websocket(ws: WebSocketAgent, data: object) -> None:
    """
    Send a semi-arbitrary python object over a websocket.

    The object is treated as json-like. When non-json-serialisable objects are encountered, they are treated as follows:
       - Datetime | Date: serialised, in place, using the isoformat text.
       - DataFrame | GeoDataFrame: Binary serialised using feather and sent as individual websocket messages.
       - Geometry [Shapely]: Binary serialised as well-known-binary and sent as individual websocket messages.

    The object is sent as a series of websocket messages as follows:
       1. Send a meta data message as serialised json. This details which binary objects are to be expected in step 3,
          after the payload.
       2. Send the payload as serialised json. This may contain substituted placeholder strings for binary serialised
          objects. Substituted strings take the form of SERIALISED_SUBSTITUTION_PREFIX{X} where x is an increasing
          index.
       3. Send any number of binary serialised objects. Each object will be a separate websocket message. The number of
          messages is deduced from first interpretting the meta data message sent in step 1.

    See _send_bytes_to_websocket for compression and the chunking of large messages.

    Parameters
    ----------
    ws : WebSocketAgent
        The Websocket Client or Server.
    data : object
        The data to be sent over the websocket.
    """
    # Traverse the object, pull out anything that needs encoding and replace with a unique key
    message, objects = _extract_objects_to_serialise(data)
    message_meta = {"binary_type_mapping": [item.serialisation_type for item in objects]}

    # Serialise all "extracted" objects
    serialised_objects = []
    for item in objects:
        if item.serialisation_type == SerialisationType.geometry:
            # Use WKB for all shapely geomtery types
            serialised_objects.append(item.data.wkb)
        elif item.serialisation_type == SerialisationType.table:
            serialised_objects.append(_serialise_dataframe(item.data))

    message_meta = json.dumps(message_meta).encode("utf-8")
    message = json.dumps(message, default=_date_serialiser).encode("utf-8")

    for item in [message_meta, message, *serialised_objects]:
        _send_bytes_to_websocket(ws, item)


def receive_object_from_websocket(ws: WebSocketAgent, timeout: float = 30) -> object:
    """
    Receive a semi-arbitrary python object over a websocket.

    This reverses the protocol employed by send_object_to_websocket:
       - Receive and decode the meta data message. This determines how many binary messages are expected after
         the payload.
       - Receive and decode the primary payload.
       - Receive each binary serialised object.
       - Deserialise each binary object and re-saturate the payload accordingly replacing any placeholder strings with
         python objects.

    Parameters
    ----------
    ws : WebSocketAgent
        The Websocket Client or Server.
    timeout : float
        If provided, will raise RuntimeError if no message is received within this number of seconds.
        By default, 30 seconds.

    Returns
    -------
    object
        The python object received via the websocket.
    """
    # Receive transmission meta data.
    message_meta = _receive_bytes_from_websocket(ws, timeout)
    message_meta = json.loads(message_meta.decode("utf-8"))
    objects_type_map = message_meta['binary_type_mapping']

    # Receive the main payload excluding binary objects
    data = _receive_bytes_from_websocket(ws, timeout)
    data = json.loads(data.decode("utf-8"))

    # Finally receive and deserialised binary objects
    deserialised_objects = []
    for object_type in objects_type_map:
        raw_object = _receive_bytes_from_websocket(ws, timeout)
        if object_type == SerialisationType.table:
            deserialised_objects.append(_deserialise_feather_bytes_to_dataframe(raw_object))
        elif object_type == SerialisationType.geometry:
            deserialised_objects.append(from_wkb(raw_object))
        del raw_object

    data = _insert_deserialised_objects(data, object_list=deserialised_objects)

    return data
