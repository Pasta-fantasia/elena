import click

from elena.config import dependency_injection
from elena.constants import VERSION


@click.command()
@click.argument('profile', default='prod', type=click.Choice(['local', 'prod']))
@click.argument('home', required=False, default=None, type=str)
def cli(profile, home):
    """
    Elena command line interface runner

    Arguments:
            profile: local, prod
            home: Elena home directory
    """
    print(f"Running Elena v{VERSION} from CLI with {str.upper(profile)} profile")
    service = dependency_injection.get_service(profile=profile, home=home)
    service.run()


if __name__ == "__main__":
    cli()
