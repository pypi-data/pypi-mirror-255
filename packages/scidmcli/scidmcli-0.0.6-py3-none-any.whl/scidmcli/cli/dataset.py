import os
import click
import json
import requests
import asyncio
from scidmcli.connection import connect_to_ckan
from scidmcli.util import isNone
from scidmcli.download import download_file


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, help='Manage dataset [list|files|download|create|push|delete]')
def cli():
    pass

@click.command(help='list the datasets of organization')
@click.option('-o', '--organization', help='the id or name of organization', required=True)
@click.option('-d', '--detail', help='the detail of dataset.', is_flag=True)
def list(organization, detail):
    with connect_to_ckan() as ckan:
        r = ckan.action.package_search(q=f'organization:{organization}')
        if detail:
            filtered_list = [key for key in r['results']]
            click.echo(filtered_list)
        else:
            filtered_list = [{key['title']: key['name']} for key in r['results']]
            click.echo(filtered_list)
            
@click.command(help='list the resources of dataset')
@click.option('-i', '--id', help='the id or name of dataset', required=True)
@click.option('-d', '--detail', help='the detail of resource.', is_flag=True)
def files(id, detail):
    with connect_to_ckan() as ckan:
        r = ckan.action.package_show(id=id)
        if detail:
            filtered_list = [key for key in r['resources']]
            click.echo(filtered_list)
        else:
            filtered_list = [key['name'] for key in r['resources']]
            click.echo(filtered_list)

@click.command(help='download the resources of dataset')
@click.option('-i', '--id', help='the id or name of dataset', required=True)
@click.option('-p', '--path', help='the path of download destination')
def download(id, path):
    with connect_to_ckan() as ckan:
        if isNone(path):
            path = os.path.join(os.path.expanduser('~'), os.environ['SCIDM_CLI_PATH'], 'download')
            if not os.path.isdir(path):
                os.mkdir(path)

            download_path = os.path.join(path, id)
            if not os.path.isdir(download_path):
                os.mkdir(download_path)

        request_header = {'Authorization': ckan.apikey}
        resp = ckan.action.package_show(id=id)
        asyncio.run(download_file(resp, request_header, download_path))
        
        
@click.command(help='create new dataset')
@click.option('-d', '--data', help='input data in JSON format', required=True)
def create(data):
    '''
    Example:
    {
        "name": "test_dataset",
        "title": "Test Dataset",
        "private": true,
        "author": "Author",
        "author_email": "author@example.com",
        "maintainer": "Maintainer",
        "maintainer_email": "maintainer@example.com",
        "owner_org": "org1"
    }
    '''
    with connect_to_ckan() as ckan:
        data_dict = json.loads(data)
        r = ckan.action.package_create(**data_dict)
        click.echo(r)

@click.command(help='upload resources')
@click.option('-d', '--data', help='input data in JSON format', required=True)
def push(data):
    '''
    Example:
    - Upload resource with URL:
        {
            "package_id": "test_dataset",
            "name": "test_resource",
            "url": "https://example.com/test_resource",
            "description": "This is a test resource.",
            "format": "csv"
        }

    - Upload resource with file:
        {
            "package_id": "test_dataset",
            "name": "test_resource",
            "upload": "/path/to/file.txt",
            "description": "This is a test resource.",
            "format": "txt"
        }
    '''
    with connect_to_ckan() as ckan:
        data_dict = json.loads(data)
        upload_url = f'{ckan.address.rstrip("/")}/api/action/resource_create'
        request_header={'Authorization': ckan.apikey}
        if data_dict.get('upload'):
            files = {'upload': (data_dict['name'], open(data_dict['upload'], 'rb'))}
            request_header['Accept'] = 'multipart/form-data'
            response = requests.post(upload_url, headers=request_header, files=files, data=data_dict)
        else:
            request_header['Accept'] = 'application/json'
            response = requests.post(upload_url, headers=request_header, json=data_dict)

        if response.ok:
            click.echo(f'Upload successfully.')
        else:
            click.echo(f'Upload failed. Response: {response.status_code} {response.text}')


@click.command(help='delete dataset or resource')
@click.option('-t', '--type', help='the type of dataset or resource', required=True, 
              type=click.Choice(['ds', 'rs']))
@click.option('-i', '--id', help='the id of dataset or resource', required=True)
def delete(type, id):
    if type == 'ds':
        with connect_to_ckan() as ckan:
            ckan.action.package_delete(id=id)
            click.echo(f'Dataset {id} deleted.')
    elif type == 'rs':
        with connect_to_ckan() as ckan:
            ckan.action.resource_delete(id=id)
            click.echo(f'Resource {id} deleted.')    
    else:
        raise ValueError('Invalid type.')
    
cli.add_command(list)
cli.add_command(files)
cli.add_command(download)
cli.add_command(create)
cli.add_command(push)
cli.add_command(delete)
