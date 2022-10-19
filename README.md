# Elena 2 (dead queen, new queen)

## Intro

(pending to adapt from v1)


## Install


Create a virtual environment, for example at `$HOME/VEs`:

```shell
python3 -m venv elena
source elena/bin/activate
pip install git+ssh://git@github.com/Ciskam-Lab/elena.git@main#egg=elena
```


## Configure

(pending to adapt from v2.0.0)

Create a user configuration YAML file at `cfg/` directory for every running profile (dev, test, prod). The values configured there will override the values on default YAML files.

So to configure some personal values for `dev` profile por example, create `dev-user.yaml` file and override the user values already defined in `dev-default.yaml`.
