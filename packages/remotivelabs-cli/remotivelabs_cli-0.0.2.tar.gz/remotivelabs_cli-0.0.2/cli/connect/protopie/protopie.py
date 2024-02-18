import json
import time
from pathlib import Path
from cli import settings
import grpc
import socketio
from remotivelabs.broker.sync import Client, SignalsInFrame, BrokerException
from rich.console import Console
from socketio.exceptions import ConnectionError as SocketIoConnectionError
from typing import Union
from rich import print as pretty_print

global PP_CONNECT_APP_NAME
PP_CONNECT_APP_NAME = "RemotiveBridge"

io = socketio.Client()

err_console = Console(stderr=True)

_has_received_signal = False


@io.on('connect')
def on_connect():
    print('Connected to protopie-connect')
    io.emit('ppBridgeApp', {'name': PP_CONNECT_APP_NAME})
    io.emit('PLUGIN_STARTED', {'name': PP_CONNECT_APP_NAME})

    global is_connected
    is_connected = True


@io.on('ppMessage')
def on_message(data):
    # Not used but possible. Could be used to send commands like start, pause, stop
    print(f"message from connect: {data}")


def _connect_to_broker():
    with open(config_path) as f:
        mapping = json.load(f)

    sub = mapping['subscription']
    signals = list(sub.keys())
    namespaces = list(map(lambda x: sub[x]['namespace'], signals))

    def on_signals(frame: SignalsInFrame):

        global _has_received_signal
        if not _has_received_signal:
            pretty_print("Bridge-app is properly receiving signals, you are good to go :thumbsup:")
            _has_received_signal = True

        for s in frame:
            sig = sub[s.name()]
            sig = sig if 'mapTo' not in sig.keys() else sig['mapTo']
            if isinstance(sig, list):
                for ss in sig:
                    io.emit("ppMessage", {'messageId': ss, 'value': str(s.value())})
            else:
                io.emit("ppMessage", {'messageId': sig, 'value': str(s.value())})

    try:
        pretty_print("Connecting and subscribing to broker...")
        subscription = None
        client = Client(client_id="cli")
        client.connect(url=broker, api_key=x_api_key)
        client.on_signals = on_signals

        subscription = client.subscribe(
            signal_names=signals,
            namespaces=namespaces,
            changed_values_only=False
        )
        pretty_print("Subscription to broker completed")
        pretty_print("Waiting for signals...")

        while True:
            time.sleep(1)

    except grpc.RpcError as e:
        err_console.print(":boom: [red]Problems connecting or subscribing[/red]")
        if isinstance(e, grpc.Call):
            print(f"{e.code()} - {e.details()}")
        else:
            print(e)

    except BrokerException as e:
        print(e)
        if subscription is not None:
            subscription.cancel()

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Closing subscription.")
        if subscription is not None:
            subscription.cancel()

    except Exception as e:
        err_console.print(f":boom: {e}")
        #exit(1)

def do_connect(address: str, broker_url: str, api_key: Union[str, None], config: Path):
    global broker
    global x_api_key
    global config_path
    broker = broker_url

    if broker_url.startswith("https"):
        if api_key is None:
            print("No --api-key, reading token from file")
            x_api_key = settings.read_token()
        else:
            x_api_key = api_key
        #    err_console.print("You must use --api-key ")
    else:
        x_api_key = api_key
    try:
        io.connect(address)
        config_path = config
        while is_connected is None:
            time.sleep(1)
        _connect_to_broker()
    except SocketIoConnectionError as e:
        err_console.print(f':boom: [bold red]Failed to connect to ProtoPie Connect[/bold red]')
        err_console.print(e)
        exit(1)
    except Exception as e:
        err_console.print(f":boom: {e}")
        exit(1)
