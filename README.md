# Elena 2 (dead queen, new queen)

## Intro

(pending to adapt from v1)


## Configuration

Elena can run on a local machine, and we're planning to run it on AWS lambdas. The way the external configuration is loaded is prepared for both running methods, loading a configuration dictionary loaded from a YAML configuration file (local) or stored at a AWS S3 file.

For external local configuration, Elena needs a local home directory with the configuration files.
1. First, Elena checks the system variable `ELENA_HOME` will be home directory
2. If not defined, the home directory is the current directory

There are tree configuration files:

### config.yaml

An optional configuration file (default values are used if not present). 
Used to override the default configuration for adaptors (logs, paths to bots files and CCTX).

- Be aware that if you override any adaptor configuration (i.e. LocalLogger), you need to define all values, not only the one you want to change.
- You can define your own Logger or MetricsManager by defining its class in the configuration file:
  - The logger class must implement the [Logger](./elena/domain/ports/logger.py) interface.
  - The logger class must implement the [MetricsManager](./elena/domain/ports/metrics_manager.py) interface.

A typical `config.yaml` file content, showing the default values:

```yaml
Logger:
  class: elena.adapters.logger.local_logger.LocalLogger
  level: INFO
  path: logs  # relative path under home directory
  max_bytes: 1000000 # 1 MB max log files size
  backup_count: 5  # Number of log backup files
MetricsManager:
  class: elena.adapters.metrics_manager.local_metrics_manager.LocalMetricsManager
LocalBotManager:
  path: bots # relative path under home directory
CctxExchangeManager:
  fetch_ohlcv_limit: 100
  fetch_ohlcv_limit_retry_every_milliseconds: 1000
```


### strategies.yaml

Used for configuring the strategies and bots to run, as well as the tags that enables or disables the bots.

A typical `strategies.yaml` file content:

```yaml
Strategies:
  - id: ExchangeBasicOperationsTest-1
    name: ExchangeBasicOperationsTest
    enabled: true
    strategy_class: test.elena.domain.services.test_elena.ExchangeBasicOperationsBot
    bots:
      - id: Exchange_Test_Ops_BTC_USDT
        name: Exchange Basic Operations Test 1 on BTC/USDT
        enabled: true
        pair: BTC/USDT
        exchange: binance
        time_frame: 1m # Valid values: 1m, 1h, 1d, 1M, 1y
        cron_expression: "*/5 * * * *" # At every 5th minute
        tags:
          - ranging
          - bear
        config:
          band_length: 13
          band_mult: 1

Tags:
  - id: bear
    enabled: true
  - id: bull
    enabled: true
  - id: ranging
    enabled: true
```

### secrets.yaml

Used for configuring the Exchange and other adaptors that requires API keys and passwords.

This config file should never be committed in a repository.

A typical `secrets.yaml` file content:

```yaml
Exchanges:
  - id: binance
    enabled: true
    sandbox_mode: true
    api_key: 7bG7TGZoM4MJT2CthNSpb3TVEAzTzGxMoASFJu4bijHPXMXoePq7hChMyXQWAFRjg
    password: not_in_use
    secret: K5fAmzNZ9ZESBd3dsHFW7iXs5CarUgGnzYfcPpr6uFBWZykdonCiiDzBTGZP7taXZ
  - id: kucoin
    enabled: false
    sandbox_mode: false
    api_key: DTJ4iLL9mQZd2JpceLeQSBTmbdLdUto7eDnxUgm5gXQ4BiDiKH5YfqBNKSPVRZQvN
    password: "faceplate-usable-gap"
    secret: hzh2tqLroRBr9hCxjH36t6GFzcW4zoqA9c4MC96rPqPP59dzdKyRUiNYqsGxkCxoQ
```

## Install

Create a virtual environment, for example at `$HOME/VEs`:

```shell
python3 -m venv elena
source elena/bin/activate
pip install -U setuptools wheel
pip install git+https://github.com/Pasta-fantasia/elena.git@main#egg=elena
```

