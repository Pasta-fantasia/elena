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