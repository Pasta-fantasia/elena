from elena.config import dependency_injection
from elena.constants import VERSION
from elena.entrypoint.local.local_config_reader import LocalConfigReader


def main():
    config = LocalConfigReader().config
    container = dependency_injection.get_container(config)
    container.wire(modules=[__name__])
    elena = container.elena()
    print(f"Starting Elena v{VERSION} from CLI")
    elena.run()


if __name__ == "__main__":
    main()
