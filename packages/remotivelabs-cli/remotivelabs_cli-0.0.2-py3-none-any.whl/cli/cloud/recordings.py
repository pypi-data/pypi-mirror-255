import glob
import json
import os
import re
import shutil
import sys
from pathlib import Path

import requests
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from . import rest_helper as rest
from ..broker.lib.broker import Broker
from ..broker.lib.errors import ErrorPrinter as error_printer

app = typer.Typer()


def uid(p):
    print(p)
    return p['uid']


# to be used in options
# autocompletion=project_names)
def project_names():
    r = requests.get(f'{rest.base_url}/api/bu/{rest.org}/project', headers=rest.headers)
    # sys.stderr.write(r.text)
    if r.status_code == 200:
        projects = r.json()
        names = map(lambda p: p['uid'], projects)
        return (list(names))
    else:
        sys.stderr.write(f"Could not list projects due to {r.status_code}\n")
        # os.kill(signal.SIGSTOP)
        raise typer.Exit(0)
        # return []

        # return map(list(r.json()), lambda e: e.uid)


#    return ["beamyhack"]


@app.command("list")
def listRecordings(is_processing: bool = typer.Option(default=False,
                                                      help="Use this option to see only those that are beeing processed or are invalid"),
                   project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    """
    List all recording sessions in a project. You can choose to see all valid recordings (default) or use
    --is-processing and you will get those that are currently beeing processed or that failed to be validated.

    """

    if is_processing:
        rest.handle_get(f"/api/project/{project}/files/recording/processing")
    else:
        rest.handle_get(f"/api/project/{project}/files/recording")


@app.command(help="Shows details about a specific recording in project")
def describe(recording_session: str = typer.Argument(..., help="Recording session id"),

             project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}")


@app.command(help="Shows details about a specific recording in project")
def copy(recording_session: str = typer.Argument(..., help="Recording session id"),
         target_project: str = typer.Option(..., help="Which project to copy the recording to"),
         project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    rest.handle_post(url=f"/api/project/{project}/files/recording/{recording_session}/copy",
                     body=json.dumps({'projectUid': target_project}))


def doStart(name: str, project: str, api_key: str, return_response: bool = False):
    if api_key == "":
        body = {"size": "S"}
    else:
        body = {"size": "S", 'apiKey': api_key}

    name = name if name is not None else 'personal'
    return rest.handle_post(f"/api/project/{project}/brokers/{name}", body=json.dumps(body),
                            return_response=return_response)


@app.command(help="Prepares all recording files and transformations to be available for playback")
def mount(recording_session: str = typer.Argument(..., help="Recording session id",
                                                  envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
          broker: str = typer.Option(None, help="Broker to use"),
          ensure_broker_started: bool = typer.Option(default=False, help="Ensure broker exists, start otherwise"),
          transformation_name: str = typer.Option("default", help="Specify a custom signal transformation to use"),
          project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        rest.ensure_auth_token()

        v = progress.add_task(description=f"Validating recording exists...", total=1)
        rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
        progress.update(v, advance=1)

        v = progress.add_task(description=f"Verifying broker exists...", total=100)

        # Handle personal broker
        if broker is None:
            r = rest.handle_get(url=f'/api/project/{project}/brokers/personal',
                                return_response=True,
                                allow_status_codes=[404])
            progress.update(v, advance=100.0)
            if r.status_code == 200:
                broker = r.json()['shortName']

            elif r.status_code == 404:
                v = progress.add_task(description=f"Starting personal broker...", total=1)
                r = doStart(None, project, '', return_response=True)
                progress.update(v, advance=1)
                if r.status_code != 200:
                    print(r.text)
                    exit(0)
                broker = r.json()['shortName']
            else:
                sys.stderr.write(f"Got http status code {r.status_code}")
                typer.Exit(0)
        # Handle specified broker
        else:
            r = rest.handle_get(url=f'/api/project/{project}/brokers/{broker}',
                                return_response=True,
                                allow_status_codes=[404])

            progress.update(v, advance=100.0)
            if r.status_code == 404:
                if ensure_broker_started:
                    v = progress.add_task(description=f"Starting broker {broker}...", total=1)
                    r = doStart(broker, project, '', return_response=True)
                    progress.update(v, advance=1.0)
                    if r.status_code != 200:
                        print(r.text)
                        exit(0)
                else:
                    print("Broker not running, use --ensure-broker-started to start the broker")
                    exit(0)
            elif r.status_code != 200:
                sys.stderr.write(f"Got http status code {r.status_code}")
                typer.Exit(0)

        progress.add_task(
            description=f"Uploading recording {recording_session} to {broker} and setting play mode to pause...",
            total=None)
        # if recording_file == "":
        #    rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}/upload",
        #                    params={'brokerName': broker})
        # else:
        broker_config_query = ""
        if (transformation_name != "default"):
            broker_config_query = f"?brokerConfigName={transformation_name}"

        rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}/upload{broker_config_query}",
                        params={'brokerName': broker}, return_response=True)
        print("Successfully mounted recording on broker")


@app.command(help="Downloads the specified recording file to disk")
def download_recording_file(
        recording_file_name: str = typer.Argument(..., help="Recording file to download"),
        recording_session: str = typer.Option(..., help="Recording session id that this file belongs to",
                                              envvar='REMOTIVE_CLOUD_RECORDING_SESSION'),
        project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description=f"Downloading {recording_file_name}", total=None)

        # First request the download url from cloud. This is a public signed url that is valid
        # for a short period of time
        rest.ensure_auth_token()
        get_signed_url_resp = requests.get(
            f'{rest.base_url}/api/project/{project}/files/recording/{recording_session}/recording-file/{recording_file_name}',
            headers=rest.headers, allow_redirects=True)
        if get_signed_url_resp.status_code == 200:

            # Next download the actual file
            download_resp = requests.get(url=get_signed_url_resp.json()["downloadUrl"], stream=True)
            if download_resp.status_code == 200:
                with open(recording_file_name, 'wb') as out_file:
                    shutil.copyfileobj(download_resp.raw, out_file)
                print(f"{recording_file_name} downloaded")
            else:
                sys.stderr.write(download_resp.text)
                sys.stderr.write(f"Got http status {download_resp.status_code}\n")
        else:
            sys.stderr.write(get_signed_url_resp.text)
            sys.stderr.write(f"Got http dd status {get_signed_url_resp.status_code}\n")


@app.command(name="delete")
def delete(recording_session: str = typer.Argument(..., help="Recording session id"),
           project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    """
    Deletes the specified recording session including all media files and configurations.

    """
    rest.handle_delete(f"/api/project/{project}/files/recording/{recording_session}")


@app.command(name="delete-recording-file")
def delete_recording_file(recording_file_name: str = typer.Argument(..., help="Recording file to download"),
                          recording_session: str = typer.Option(...,
                                                                help="Recording session id that this file belongs to",
                                                                envvar='REMOTIVE_CLOUD_RECORDING_SESSION'),
                          project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    """
    Deletes the specified recording file

    """
    rest.handle_delete(
        f'/api/project/{project}/files/recording/{recording_session}/recording-file/{recording_file_name}')


@app.command()
def upload(
        path: Annotated[
            Path,
            typer.Argument(
                exists=True,
                file_okay=True,
                dir_okay=False,
                writable=False,
                readable=True,
                resolve_path=True,
                help="Path to recording file to upload"
            ),
        ],
        project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT'),
        recording_type: str = typer.Option("remotive-broker", help="Type of recording"),
        signal_database: str = typer.Option(None, help="Signal database to use with candump")):
    # TODO - Test to do this with typer Enums instead
    # Validate this here to validate before we start any progress
    if recording_type == "candump" and (signal_database is None or signal_database == ""):
        error_printer.print_hint("Option --signal-database is required with --recording-type is 'candump'")
        exit(1)
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description=f"Uploading {path}", total=None)

        filename = os.path.basename(path.name)
        rest.ensure_auth_token()

        if recording_type == "candump":
            rest.headers["x-recording-type"] = "candump"
            r = rest.handle_post(url=f"/api/project/{project}/files/recording/{filename}",
                                 return_response=True,
                                 body=json.dumps({'dbcFile': signal_database}))
        else:
            r = rest.handle_post(f"/api/project/{project}/files/recording/{filename}", return_response=True)
            headers = {}
            # TODO - Fix correct content-type
            headers["content-type"] = "application/x-www-form-urlencoded"
            with open(path, 'rb') as f:
                response = requests.put(r.text, f, headers=headers)
                if response.status_code >= 200 and response.status_code < 300:
                    print("File successfully uploaded, please run 'remotive cloud recordings list' "
                          "to verify that the recording was successfully processed")
                else:
                    rest.err_console.print(f':boom: [bold red]Got status code[/bold red]: {response.status_code}')


@app.command()
def upload_broker_configuration(
        directory: str = typer.Argument(..., help="Configuration directory"),
        recording_session: str = typer.Option(..., help="Recording session id",
                                              envvar='REMOTIVE_CLOUD_RECORDING_SESSION'),
        project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT'),
        overwrite: bool = typer.Option(False, help="Overwrite existing configuration if it exists")
):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:

        # Must end with /
        if not directory.endswith("/"):
            directory = f'{directory}/'

        #
        # List files in specified directory. Look for interfaces.json and use that directory where this is located
        # as configuration home directory
        #
        files = list(filter(lambda item: "interfaces.json" in item, glob.iglob(directory + '**/**', recursive=True)))
        if len(files) == 0:
            sys.stderr.write("No interfaces.json found in directory, this file is required")
            raise typer.Exit(1)
        if len(files) > 1:
            sys.stderr.write(f"{len(files)} interfaces.json found in directoryw which is not supported")
            raise typer.Exit(1)
        broker_config_dir_name = os.path.dirname(files[0]).rsplit('/', 1)[-1]

        #
        # Get the current details about broker configurations to see if a config with this
        # name already exists
        #
        task = progress.add_task(description=f"Preparing upload of {broker_config_dir_name}", total=1)
        details_resp = rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}",
                                       return_response=True)
        details = details_resp.json()
        existing_configs = details['brokerConfigurations']
        if (len(existing_configs) > 0):
            data = list(filter(lambda x: x['name'] == broker_config_dir_name, existing_configs))
            if len(data) > 0:
                if (overwrite):
                    rest.handle_delete(
                        f'/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_dir_name}',
                        quiet=True)
                else:
                    sys.stderr.write("Broker configuration already exists, use --overwrite to replace\n")
                    raise typer.Exit(1)

        #
        # From the list of files, create a tuple of local_path to the actual file
        # and a remote path as it should be stored in cloud
        #
        file_infos = list(map(lambda item:
                              {'local_path': item,
                               'remote_path': f"/{broker_config_dir_name}{item.rsplit(broker_config_dir_name, 1)[-1]}"},
                              glob.iglob(directory + '**/*.*', recursive=True)))

        #
        # convert this remote paths and ask cloud to prepare upload urls for those
        #
        json_request_upload_urls_req = {
            'name': 'not_used',
            'paths': list(map(lambda x: x['remote_path'], file_infos))
        }

        response = rest.handle_put(url=f'/api/project/{project}/files/recording/{recording_session}/configuration',
                                   return_response=True, body=json.dumps(json_request_upload_urls_req))
        if (response.status_code != 200):
            print(f'Failed to prepare configuration upload')
            print(f'{response.text} - {response.status_code}')
            raise typer.Exit(1)
        progress.update(task, advance=1)

        task = progress.add_task(description=f"Uploading {broker_config_dir_name} ({len(file_infos)} files)",
                                 total=len(file_infos))

        #
        # Upload urls is a  remote_path : upload_url dict
        # '/my_config/interfaces.json' : "<upload_url>"
        #
        upload_urls = json.loads(response.text)

        # For each file - upload
        for file in file_infos:
            key = file['remote_path']
            path = file['local_path']
            url = upload_urls[key]
            upload_task = progress.add_task(description=f"Uploading {key}", total=1)
            headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
            r = requests.put(url, open(path, 'rb'), headers=headers)
            progress.update(task, advance=1)
            if r.status_code != 200:
                print("Failed to upload broker configuration")
                print(r.status_code)
                print(r.text)
                typer.Exit(1)
            progress.update(upload_task, advance=1)

        print(f"Successfully uploaded broker configuration {broker_config_dir_name}")


@app.command(help="Downloads the specified broker configuration directory as zip file")
def download_configuration(
        broker_config_name: str = typer.Argument(..., help="Broker config name"),
        recording_session: str = typer.Option(..., help="Recording session id",
                                              envvar='REMOTIVE_CLOUD_RECORDING_SESSION'),
        project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')
):
    rest.ensure_auth_token()
    r = rest.handle_get(
        url=f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_name}",
        return_response=True)
    filename = get_filename_from_cd(r.headers.get('content-disposition'))
    open(filename, 'wb').write(r.content)
    print(f'Downloaded file {filename}')


@app.command(help="Downloads the specified broker configuration directory as zip file")
def delete_configuration(
        broker_config_name: str = typer.Argument(..., help="Broker config name"),
        recording_session: str = typer.Option(..., help="Recording session id",
                                              envvar='REMOTIVE_CLOUD_RECORDING_SESSION'),
        project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')
):
    rest.handle_delete(
        url=f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_name}")


@app.command(help="Copy recording to another project")
def copy(recording_session: str = typer.Argument(..., help="Recording session id"),
         project: str = typer.Option(..., help="Project to import sample recording into",
                                     envvar='REMOTIVE_CLOUD_PROJECT'),
         destination_project: str = typer.Option(..., help="Destination project")):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        v = progress.add_task(description=f"Copying recording to {destination_project}, may take a few seconds...",
                              total=100)
        rest.handle_post(url=f"/api/project/{project}/files/recording/{recording_session}/copy",
                         body=json.dumps({'projectUid': destination_project}))
        progress.update(v, advance=100.0)


@app.command()
def play(recording_session: str = typer.Argument(..., help="Recording session id"),
         broker: str = typer.Option(None, help="Broker to use"),
         project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    _do_change_playback_mode("play", recording_session, broker, project)


@app.command()
def pause(recording_session: str = typer.Argument(..., help="Recording session id"),
          broker: str = typer.Option(None, help="Broker to use"),
          project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    _do_change_playback_mode("pause", recording_session, broker, project)


@app.command()
def seek(recording_session: str = typer.Argument(..., help="Recording session id"),
         seconds: int = typer.Option(..., min=0, help="Target offset in seconds"),
         broker: str = typer.Option(None, help="Broker to use"),
         project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    _do_change_playback_mode("seek", recording_session, broker, project, seconds)


@app.command()
def stop(recording_session: str = typer.Argument(..., help="Recording session id"),
         broker: str = typer.Option(None, help="Broker to use"),
         project: str = typer.Option(..., help="Project ID", envvar='REMOTIVE_CLOUD_PROJECT')):
    _do_change_playback_mode("seek", recording_session, broker, project, 0)


def _do_change_playback_mode(mode: str, recording_session: str, broker: str, project: str, seconds: int = None):
    response = rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
    r = json.loads(response.text)
    recordings: list = r["recordings"]
    files = list(map(lambda rec: {'recording': rec['fileName'], 'namespace': rec['metadata']['namespace']}, recordings))

    if broker is not None:
        response = rest.handle_get(f"/api/project/{project}/brokers/{broker}", return_response=True)
    else:
        response = rest.handle_get(f"/api/project/{project}/brokers/personal", return_response=True)
    broker_info = json.loads(response.text)
    broker = Broker(broker_info['url'], None)
    if mode == "pause":
        broker.pause_play(files)
    elif mode == "play":
        broker.play(files)
    elif mode == "seek":
        broker.seek(files, int(seconds * 1000000))
    else:
        raise Exception("Illegal command")


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]
