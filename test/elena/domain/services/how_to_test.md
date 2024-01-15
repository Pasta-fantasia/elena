# Test strategy

We record real exchange data on fake_exchange_manager to be able to run tests in the future without connecting to a real exchange.
For testing with real exchange data, we need to create a configuration that uses the real exchange API key:
- All test configuration is in `test/elena/domain/services/test_home` directory
- Rename `secrets-sample.yaml` to `secrets.yaml`
- Add a Binance testnet API key (https://testnet.binance.vision/)

When all data is recorded, we can:
- remove `test/elena/domain/services/test_home/secrets.yaml`
- remove the .gitignore entry for `test/elena/domain/services/test_home/secrets.yaml`
