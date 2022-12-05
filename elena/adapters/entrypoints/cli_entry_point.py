from dependency_injector.wiring import Provide, inject

from elena.config.dependency_injection import Container
from elena.constants import VERSION
from elena.domain.services.elena import Elena


@inject
def main(elena: Elena = Provide[Container.elena]) -> None:
    print(f"Starting Elena v{VERSION} from CLI")
    elena.run()


if __name__ == "__main__":
    container = Container()
    container.wire(modules=[__name__])
    main()
