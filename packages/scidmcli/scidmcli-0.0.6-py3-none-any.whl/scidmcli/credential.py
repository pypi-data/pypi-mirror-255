import os
import yaml
from scidmcli.util import isNone, isFile
from terminaltables import AsciiTable 
from collections import defaultdict


class Credential(object):

    # Credential class to manage API credentials
    def __init__(self, scidm_api_key=None):
        self.scidm_data_path = Credential._getScidmDataPath()
        self.scidm_credential = Credential._getCredential()
        self.scidm_api_key = scidm_api_key
        self.server_url = 'https://scidm.nchc.org.tw/'
        if isNone(scidm_api_key):
            self.loadCredential()
        else:
            self.initCredential()

    def __str__(self):
        table_info = [['key', 'value']] + [[key, value] for key, value in vars(self).items()]
        table = AsciiTable(table_info)
        return table.table
    
    def initCredential(self):
        # Initialize credential file
        with open(self.scidm_credential, 'w') as fn:
            yaml.safe_dump(Credential._initCredentialData(self.scidm_api_key, self.server_url), 
                           fn, encoding='utf-8', allow_unicode=True)

    def loadCredential(self):
        # Load credential from file
        if Credential._isValidCredential():
            config = yaml.load(open(self.scidm_credential, 'r').read(), Loader=yaml.SafeLoader)
            if isNone(config):
                raise ValueError(f'{self.scidm_credential} is not a valid credentials file')

            self.scidm_api_key = config['default']['scidm_api_key']
            self.server_url = config['default']['server_url']

    @staticmethod
    def _getScidmDataPath():
        # Get SCIDM data path
        if 'SCIDM_CLI_PATH' in os.environ:
            return os.environ['SCIDM_CLI_PATH']
        else:
            return os.path.dirname(os.path.realpath(__file__))
    
    @staticmethod
    def _getCredential():
        # Get credential file path
        return os.path.join(Credential._getScidmDataPath(), 'credential')
    
    @staticmethod
    def _isValidCredential():
        # Check if credential file is valid
        scidm_credential = Credential._getCredential()
        if not isNone(scidm_credential) and isFile(scidm_credential):
            config = yaml.load(open(scidm_credential, 'r').read(), Loader=yaml.SafeLoader)
            if not isNone(config):
                return True
        return False
    
    @staticmethod
    def _initCredentialData(apikey, url):
        # Initialize credential data
        data = defaultdict(dict)
        data['default']['scidm_api_key'] = apikey
        data['default']['server_url'] = url

        return dict(data)

    @staticmethod
    def _getAPIConfig():
        # Get API key and URL
        if Credential._isValidCredential():
            config = yaml.load(open(Credential._getCredential(), 'r').read(), Loader=yaml.SafeLoader)
            return config['default']['scidm_api_key'], config['default']['server_url']
        
        raise ValueError('Invalid credential')
