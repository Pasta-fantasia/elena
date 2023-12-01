try:
    from importlib.metadata import version
except ImportError:
    # For Python versions prior to 3.8
    from importlib_metadata import version

try:
    __version__ = version('elena')
except Exception as e:
    __version__ = '2.1.0-SNAPSHOT'
    print(f"Error retrieving version: {e}")
