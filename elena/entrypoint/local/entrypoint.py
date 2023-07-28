from elena.adapters.config.local_config_reader import LocalConfigReader
from elena.config import dependency_injection
from elena import __version__ as version


def main():
    config = LocalConfigReader().config
    container = dependency_injection.get_container(config)
    container.wire(modules=[__name__])
    elena = container.elena()
    print(f"Starting Elena v{version} from CLI")
    elena.run()


if __name__ == "__main__":
    main()
