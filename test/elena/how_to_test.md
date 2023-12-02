# Test strategy

We record real exchange data on fake_exchange_manager to be able to run tests in the future without connecting to a real exchange.
For testing with real exchange data, we need to create a configuration that uses the real exchange API key:
- Rename `elena_config_sample.yaml` to elena_config.yaml
- add binance API key (https://testnet.binance.vision/)

When all data is recorded, we can:
- remove `/test/elena/elena_config.yaml`
- rename `/test/elena/elena_config_sample.yaml` to `/test/elena/elena_config.yaml`
- remove the .gitignore entry for `/test/elena/elena_config.yaml`


