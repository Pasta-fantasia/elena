from typing import Optional

from elena import __version__ as version
from elena.adapters.config.local_config_reader import LocalConfigReader
from elena.config import dependency_injection


def main(home: Optional[str] = None):
    config = LocalConfigReader(home).config
    container = dependency_injection.get_container(config)
    container.wire(modules=[__name__])
    elena = container.elena()
    container.logger().info("Starting Elena v%s from CLI", version)
    elena.run()


if __name__ == "__main__":
    main()
