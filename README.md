# Elena 2 (dead queen, new queen)

## Intro

(pending to adapt from v1)


## Configuration

Elena can run on a local machine and we're planning to run it on AWS lambdas. The way the external configuration is loaded is prepared for both running methods, loading a configuration dictionary loaded from a YAML configuration file (local) or stored at a AWS S3 file.

For external local configuration, Elena needs a local home directory with the configuration defined at `elena_config.yaml` file.
1. First, Elena checks the system variable `ELENA_HOME` will be home directory
3. If not defined, the home directory is the current directory

A typical `elena_config.yaml` file content:

```yaml
Strategies:
   - id: SAMPLE-1
     name: Sample strategy 1
     enabled: true
     strategy_class: elena_sample.strategies.trailing_stop.Tr
     bots:
        - id: SAM-1.1
          name: Sample strategy 1 bot 1
          enabled: true
          pair: ETH/USDT
          exchange: kucoin
          tags:
             - ranging
             - bear
          config:
             key1: value1
             key2: value2
        - id: SAM-1.2
          name: Sample strategy 1 bot 2
          enabled: false
          pair: BTC/USDC
          exchange: bitget
          tags:
             - bull
          config:
             key1: value1
             key2: value2
Exchanges:
   - id: bitget
     enabled: true
     sandbox_mode: true
     api_key: ***REMOVED***
     password: ***REMOVED***
     secret: ***REMOVED***
   - id: kucoin
     enabled: false
     sandbox_mode: false
     api_key: ***REMOVED***
     password: ***REMOVED***
     secret: ***REMOVED***
Tags:
   - id: bear
     enabled: true
   - id: bull
     enabled: false
   - id: ranging
     enabled: true
```

The default configuration id defined at `elena/config/default_config.yaml` and you can override any default configuration value defining the same key in at `external_config.yaml`.

## Install

Create a virtual environment, for example at `$HOME/VEs`:

```shell
python3 -m venv elena
source elena/bin/activate
pip install git+ssh://git@github.com/Ciskam-Lab/elena.git@main#egg=elena
```


## Cycle flow

1. Load config
2. For every enabled StrategyManager
3. For every enabled bot with at least one enabled tag
4. Retrieve the bot from disk and instantiate it
5. ExchangeManager:
   1. Read the bot orders status
   2. The exchange data if required
6. Run `next()` method
7. Persist the bot to disk