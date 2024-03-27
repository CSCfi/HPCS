# Parse configuration file
from configparser import ConfigParser, NoSectionError, NoOptionError

def parse_configuration(path : str):
    config = ConfigParser()
    config.read(path)
    
    if not 'supercomputer' in config:
        raise NoSectionError("supercomputer section missing in configuration file, aborting")
    
    if not 'spire-server' in config:
        raise NoSectionError("hpcs-server section missing in configuration file, aborting")
    
    if not 'hpcs-server' in config:
        raise NoSectionError("hpcs-server section missing in configuration file, aborting")
    
    if not 'vault' in config:
        raise NoSectionError("vault section missing in configuration file, aborting")
    
    if not 'address' in config['supercomputer'] or not 'username' in config['supercomputer']:
        raise NoOptionError("'spire-server' section is incomplete in configuration file, aborting")
    
    if not 'address' in config['spire-server'] or not 'port' in config['spire-server'] or not 'trust-domain' in config['spire-server']:
        raise NoOptionError("'spire-server' section is incomplete in configuration file, aborting")
    
    if not 'url' in config['hpcs-server']:
        raise NoOptionError("'hpcs-server' section is incomplete in configuration file, aborting")
    
    if not 'url' in config['vault']:
        raise NoOptionError("'vault' section is incomplete in configuration file, aborting")
        
    return config