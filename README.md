# Elena 2 (dead queen, new queen)

## Intro

(pending to adapt from v1)


## Install

Download code

```shell
cd
git clone git@github.com:Ciskam-Lab/elena.git
```

Create a virtual environment, for example at `$HOME/VEs/timenet`:

```shell
cd
mkdir VEs
cd VEs
python -m venv elena
```

Install requirements:

```shell
cd
cd elena
source ../VEs/elena/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements.txt
deactivate
```


## Run

Run automatically every minute

- Edit cron with: `crontab -e`

Example with a VE on `$HOME/VEs/timenet` and elena downloaded at `$HOME/VEs/timenet`:

```shell
# Run Elena every minute
* * * * * $HOME/VEs/elena/bin/python $HOME/elena/cli-entry-point.py prod
```

## Configure

Create a user configuration YAML file at `cfg/` directory for every running profile (dev, test, prod). The values configured there will override the values on default YAML files.

So to configure some personal values for `dev` profile por example, create `dev-user.yaml` file and override the user values already defined in `dev-default.yaml`.
