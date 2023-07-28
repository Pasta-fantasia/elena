# import configparser
#
# config = configparser.ConfigParser()
# config.read('setup.cfg')
#
# __version__ = config.get('metadata', 'version')

# TODO: learn how to read it from setup.cfg in the right way (nt using pkg_resources)

try:
    import pkg_resources  # part of setuptools
    __version__ = pkg_resources.require("elena")[0].version
except:
    __version__ = '2-local'
