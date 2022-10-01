import click

from cfg import dependency_injection
from elena.constants import VERSION


@click.command()
@click.argument('profile', default='prod', type=click.Choice(['dev', 'test', 'prod']))
def cli(profile):
    """
    Elena command line interface runner

    Arguments:
            profile: dev, test, prod
    """
    print(f"Running Elena v{VERSION} from CLI with {profile} profile")
    service = dependency_injection.get_service(profile)
    service.run()


if __name__ == "__main__":
    cli()
