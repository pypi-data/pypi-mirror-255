"""
An integrated test for websocket transmission as used within Geostore and MalardClient.

Here, we create and then start an extremely simple flask server and then send a message to it over a websocket.
Crucially, the message must be larger than 1 MB in order to test the framing properly.

After receiving the message, the flask server will immediately send it back again. We expect to receive it unchanged.

"""
from __future__ import annotations

from datetime import datetime
from multiprocessing import Process
import os
import pickle
from sys import getsizeof
from time import perf_counter
from time import sleep
from typing import Dict

from flask import Flask
from flask import request
from geopandas import GeoDataFrame
import numpy as np
import pandas as pd
import pytest
import requests
from shapely import Point
import simple_websocket

from specklia import _websocket_helpers as websocket_helpers


@pytest.fixture()
def example_dataframe() -> pd.DataFrame:
    np.random.seed(2501)
    return pd.DataFrame({
        'lat': np.random.rand(5000),
        'lon': np.random.rand(5000),
        'timestamp': np.random.randint(1000, 2000, 5000)
    })


@pytest.fixture()
def test_netcdf_filepath(test_inputs_path: str) -> str:
    return os.path.join(test_inputs_path, 'netcdf', 'test_swath_c_oib_unc_479889082.nc')


def start_api_in_separate_process(flask_app: Flask, api_config: Dict, block_until_api_exits: bool = False) -> Process:
    """Start the API in a separate process.

    Used mainly for testing

    Parameters
    ----------
    flask_app : Flask
        The Flask app containing the API
    api_config : Dict
        The section of the config dictionary under the heading "api"
    block_until_api_exits : bool
        if true, blocks continued execution of geostore until the API kills itself.

    Returns
    -------
    Process
        The separate process running the API.
    """
    # recreate the process just in case it was previously stopped
    server_process = Process(
        target=lambda: flask_app.run(
            host=api_config['test_host_name'], port=api_config['test_port'],
            debug=True, use_reloader=False))

    server_process.start()

    # always block until the server is ready to handle requests
    is_server_ready = False
    while not is_server_ready:
        try:
            requests.get(f"http://localhost:{api_config['test_port']}/", timeout=5)
            is_server_ready = True
        except requests.exceptions.ConnectionError:
            pass

    # if the user has requested it, block until the server kills itself
    if block_until_api_exits:
        while server_process.is_alive():
            sleep(1)

    return server_process


def stop_api_in_separate_process(flask_process: Process) -> None:
    """
    Shutdown the API if it is running in a separate process.

    Parameters
    ----------
    flask_process : Process
        The process in which the API is running.
    """
    flask_process.terminate()
    flask_process.join()


def handle_websocket_message(nb_messages: str = '3'):
    ws = simple_websocket.Server(request.environ)
    nb_messages = int(nb_messages)
    received_bytes = []
    for _ in range(nb_messages):
        received_bytes.append(websocket_helpers._receive_bytes_from_websocket(ws))
    for i in range(nb_messages):
        websocket_helpers._send_bytes_to_websocket(ws, received_bytes[i])
    ws.close()
    return ''


def crash_while_handling_websocket_message():
    print('crash_while_handling_websocket_message triggered')
    ws = simple_websocket.Server(request.environ)
    websocket_helpers.receive_object_from_websocket(ws)
    sleep(100)  # simulate a crash in a separate service


@pytest.fixture()
def _bent_pipe_server() -> None:
    # create the "bent pipe" - a server that just returns what it receives
    app = Flask('websocket_bent_pipe')
    app.add_url_rule('/endpoint/<nb_messages>', None, handle_websocket_message, websocket=True)
    app.add_url_rule('/broken_endpoint', None, crash_while_handling_websocket_message, websocket=True)
    api_process = start_api_in_separate_process(
        flask_app=app, api_config={'test_host_name': '127.0.0.1', 'test_port': 9066})
    try:
        # Run tests against the server
        yield
    finally:
        stop_api_in_separate_process(api_process)


@pytest.mark.usefixtures(_bent_pipe_server.__name__)
def test_websocket_transmission(example_dataframe: pd.DataFrame):
    # send a message to the "bent pipe"
    # give it some structure so we can check the serialisation
    data_to_send = example_dataframe
    data_size_bytes = getsizeof(data_to_send)

    start_time = perf_counter()
    # Expect 3 messages: meta, message_body, binary
    ws_url = 'ws://127.0.0.1:9066/endpoint/3'
    websocket_helpers.validate_websocket_endpoint_url(ws_url)
    ws = simple_websocket.Client(ws_url)

    websocket_helpers.send_object_to_websocket(ws, data_to_send)
    received_data = websocket_helpers.receive_object_from_websocket(ws)

    end_time = perf_counter()
    pd.testing.assert_frame_equal(data_to_send, received_data)
    print('effective data rate (localhost to localhost): '
          f'{data_size_bytes * 8 / (1024 ** 2) / (end_time-start_time)} Mbps')


@pytest.mark.usefixtures(_bent_pipe_server.__name__)
def test_websocket_transmission_geometry():
    data_to_send = Point(1, 0)
    ws_url = 'ws://127.0.0.1:9066/endpoint/3'
    ws = simple_websocket.Client(ws_url)
    websocket_helpers.send_object_to_websocket(ws, data_to_send)
    received_data = websocket_helpers.receive_object_from_websocket(ws)
    assert received_data == data_to_send


@pytest.mark.usefixtures(_bent_pipe_server.__name__)
def test_websocket_transmission_datetime():
    data_to_send = datetime(2001, 1, 1)
    ws_url = 'ws://127.0.0.1:9066/endpoint/2'
    ws = simple_websocket.Client(ws_url)
    websocket_helpers.send_object_to_websocket(ws, data_to_send)
    received_data = websocket_helpers.receive_object_from_websocket(ws)
    assert received_data == data_to_send


@pytest.mark.usefixtures(_bent_pipe_server.__name__)
def test_websocket_transmission_emptydatetime():
    data_to_send = pd.DataFrame()
    ws_url = 'ws://127.0.0.1:9066/endpoint/3'
    ws = simple_websocket.Client(ws_url)
    websocket_helpers.send_object_to_websocket(ws, data_to_send)
    received_data = websocket_helpers.receive_object_from_websocket(ws)
    pd.testing.assert_frame_equal(data_to_send, received_data)


@pytest.mark.usefixtures(_bent_pipe_server.__name__)
def test_websocket_transmission_large_files(example_dataframe: pd.DataFrame):
    # send a large message to the "bent pipe"
    data_to_send = example_dataframe
    original_data_size = data_to_send.memory_usage(index=True, deep=True).sum()
    # make sure the message is at least 2 GB in size, to properly stress the transfer.
    data_to_send = pd.concat([data_to_send] * int(np.ceil((2.5 * 1024 ** 3) / original_data_size)))
    data_size_bytes = getsizeof(data_to_send)

    start_time = perf_counter()
    ws_url = 'ws://127.0.0.1:9066/endpoint/3'
    websocket_helpers.validate_websocket_endpoint_url(ws_url)
    ws = simple_websocket.Client(ws_url)

    websocket_helpers.send_object_to_websocket(ws, data_to_send)
    received_data = websocket_helpers.receive_object_from_websocket(ws)

    end_time = perf_counter()
    pd.testing.assert_frame_equal(data_to_send, received_data)
    print('effective data rate (localhost to localhost): '
          f'{data_size_bytes * 8 / (1024 ** 2) / (end_time-start_time)} Mbps')


@pytest.mark.usefixtures(_bent_pipe_server.__name__)
def test_broken_websocket_transmission(example_dataframe: pd.DataFrame):
    data_to_send = {'A': example_dataframe}
    ws_url = 'ws://127.0.0.1:9066/broken_endpoint'
    websocket_helpers.validate_websocket_endpoint_url(ws_url)
    ws = simple_websocket.Client(ws_url)

    websocket_helpers.send_object_to_websocket(ws, data_to_send)
    with pytest.raises(RuntimeError, match="Attempted to receive from a websocket, but nothing was sent."):
        websocket_helpers.receive_object_from_websocket(ws, timeout=1)


def test_serialise_deserialise_dataframe():
    df = pd.DataFrame({"A": [1, 2]})
    feather_bytes = websocket_helpers._serialise_dataframe(df)
    assert isinstance(feather_bytes, bytes)
    df_deserialised = websocket_helpers._deserialise_feather_bytes_to_dataframe(feather_bytes)
    pd.testing.assert_frame_equal(df, df_deserialised)


def test_serialise_deserialise_empty_dataframe():
    df = pd.DataFrame()
    feather_bytes = websocket_helpers._serialise_dataframe(df)
    assert isinstance(feather_bytes, bytes)
    df_deserialised = websocket_helpers._deserialise_feather_bytes_to_dataframe(feather_bytes)
    pd.testing.assert_frame_equal(df, df_deserialised)


def test_serialise_deserialise_geodataframe():
    gdf = GeoDataFrame({"geometry": [Point(1, 0)]})
    feather_bytes = websocket_helpers._serialise_dataframe(gdf)
    assert isinstance(feather_bytes, bytes)
    df_deserialised = websocket_helpers._deserialise_feather_bytes_to_dataframe(feather_bytes)
    pd.testing.assert_frame_equal(gdf, df_deserialised)


@pytest.mark.parametrize(
    ('data', 'substituted_data', 'extracted_objects'),
    [(["a", 1], ["a", 1], []),
     ({"a": 1.1}, {"a": 1.1}, []),
     (["a", {"a": 1.1}], ["a", {"a": 1.1}], []),
     ({"a": {"b": "hello"}}, {"a": {"b": "hello"}}, []),
     ({"a": {"b": pd.DataFrame({"A": [1, 2]}), "c": pd.DataFrame({"A": [3, 4]})}},
      {"a": {"b": f"{websocket_helpers.SERIALISED_SUBSTITUTION_PREFIX}1",
             "c": f"{websocket_helpers.SERIALISED_SUBSTITUTION_PREFIX}2"}},
      [websocket_helpers.SerialisationData(serialisation_type=websocket_helpers.SerialisationType.table,
                                           data=pd.DataFrame({"A": [1, 2]})),
       websocket_helpers.SerialisationData(serialisation_type=websocket_helpers.SerialisationType.table,
                                           data=pd.DataFrame({"A": [3, 4]}))]
      ),
     (Point(1, 0), f"{websocket_helpers.SERIALISED_SUBSTITUTION_PREFIX}1",
      [websocket_helpers.SerialisationData(serialisation_type=websocket_helpers.SerialisationType.geometry,
                                           data=Point(1, 0))]),
     (GeoDataFrame({"geometry": [Point(1, 0)]}), f"{websocket_helpers.SERIALISED_SUBSTITUTION_PREFIX}1",
      [websocket_helpers.SerialisationData(serialisation_type=websocket_helpers.SerialisationType.table,
                                           data=GeoDataFrame({"geometry": [Point(1, 0)]}))]),
     (pd.DataFrame(), f"{websocket_helpers.SERIALISED_SUBSTITUTION_PREFIX}1",
      [websocket_helpers.SerialisationData(serialisation_type=websocket_helpers.SerialisationType.table,
                                           data=pd.DataFrame())])
     ])
def test_extract_and_replace_serialisable_objects(data: object, substituted_data: object, extracted_objects: object):
    # Test both the extraction of objects and the re-insertion of objects in one test.
    converted_data, objects_dict = websocket_helpers._extract_objects_to_serialise(data)
    assert converted_data == substituted_data
    # Use pickle here to handle various object types easily.
    assert pickle.dumps(objects_dict) == pickle.dumps(extracted_objects)
    # Now reverse the process
    deserialised_objects = [item.data for item in objects_dict]
    final_data = websocket_helpers._insert_deserialised_objects(converted_data, deserialised_objects)
    # To handle dataframe comparisons, simply compare encoded objects.
    assert pickle.dumps(final_data) == pickle.dumps(data)
