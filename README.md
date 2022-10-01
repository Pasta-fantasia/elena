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


## Run automatically every minute

- [Cron expression generator](https://crontab.cronhub.io/)
- Edit with: `crontab -e`

Example with a VE on `$HOME/VEs/timenet` and elena downloaded at `$HOME/VEs/timenet`:

```shell
# Run Elena every minute
* * * * * $HOME/VEs/elena/bin/python $HOME/elena/cli-entry-point.py prod
```

