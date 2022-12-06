# Elena 2 (dead queen, new queen)

## Intro

(pending to adapt from v1)


## Configuration

Elena can run on a local machine and we're planning to run it on AWS lambdas. The way the external configuration is loaded is prepared for both running methods, loading a configuration dictionary loaded from a YAML configuration file (local) or stored at a AWS S3 file.

For external local configuration, Elena needs a local home directory with the configuration defined at `external_config.yaml` file.
1. First, Elena checks the system variable `ELENA_HOME` will be home directory
3. If not defined, the home directory is the current directory

A typical `external_config.yaml` file content:

```yaml
Strategies:
  -
    strategy_id: SAMPLE-1
    name: Sample strategy 1
    enabled: false
    bots:
      -
        bot_id: SAM-1.1
        name: Sample strategy 1 bot 1
        enabled: true
        pair: ETH/USDT
        config:
          key1: value1
          key2: value2
      -
        bot_id: SAM-1.2
        name: Sample strategy 1 bot 2
        enabled: false
        pair: BTC/USDC
        config:
          key1: value1
          key2: value2
Market:
  exchanges:
    -
      name: KuCoin
      API-KEY: ***REMOVED***
      enabled: false
```

The default configuration id defined at `elena/config/default_config.yaml` and you can override any default configuration value defining the same key in at `external_config.yaml`.

## Install

Create a virtual environment, for example at `$HOME/VEs`:

```shell
python3 -m venv elena
source elena/bin/activate
pip install git+ssh://git@github.com/Ciskam-Lab/elena.git@main#egg=elena
```


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