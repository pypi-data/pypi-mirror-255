from ckanapi import RemoteCKAN
from scidmcli.credential import Credential
from scidmcli.util import isNone, validate


# Connect to CKAN API
def connect_to_ckan():
    api_key, server_url = Credential._getAPIConfig()
    
    if isNone(api_key) or len(api_key) == 0 or not validate(api_key):
        raise ValueError('Invalid API key.')
    elif isNone(server_url) or len(server_url) == 0:
        raise ValueError('Invalid server url.')
    
    return RemoteCKAN(server_url, apikey=api_key)
