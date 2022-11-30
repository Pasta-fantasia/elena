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

## Configure

Create a user configuration YAML file at `cfg/` directory for every running profile (dev, test, prod). The values configured there will override the values on default YAML files.

So to configure some personal values for `dev` profile por example, create `dev-user.yaml` file and override the user values already defined in `dev-default.yaml`.


## General flow

1. Cargamos los estados de los tags de la persistencia
2. Cargamos la configuración
3. Por cada Strategy definidfa en la config
4. Por cada bot de la strategy
   1. Verificamos que el tag esté activo
   2. Recuperar la estructura de Strategy y la instanciamos
   3. MarketReader:
      1. El estado de las órdenes del bot
      1. Si es necesario, leemos la serie de datos
   4. Ejecutar el método `next()` de la Strategy
   5. Persistir la estructura de la instancia de Strategy