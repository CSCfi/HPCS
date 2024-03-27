from configparser import ConfigParser, NoSectionError, NoOptionError

def parse_configuration(path : str):
    config = ConfigParser()
    config.read(path)
    
    if not 'spire-server' in config:
        raise NoSectionError("spire-server section missing, aborting")
    
    if not 'vault' in config:
        raise NoSectionError("vault section missing, aborting")
    
    if not 'address' in config['spire-server'] or not 'port' in config['spire-server'] or not 'trust-domain' in config['spire-server']:
        raise NoOptionError("'spire-server' section is incomplete, aborting")
    
    if not 'url' in config['vault'] or not 'server-role' in config['vault']:
        raise NoOptionError("'vault' section is incomplete, aborting")
        
    return config