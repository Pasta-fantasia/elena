import ccxt

from elena.domain.model.exchange import ExchangeType, Exchange
from elena.domain.ports.logger import Logger

_connect_mapper = {
    ExchangeType.bitget: ccxt.bitget,
    ExchangeType.kucoin: ccxt.kucoin
}


def connect(exchange: Exchange, logger: Logger):
    logger.debug('Connecting to %s ...', exchange.id.value)
    _conn = _connect_mapper[exchange.id]({
        'apiKey': exchange.api_key,
        'password': exchange.password,
        'secret': exchange.secret,
    })
    _conn.set_sandbox_mode(exchange.sandbox_mode)
    logger.info('Connected to %s at %s', exchange.id.value, _conn.urls['api']['public'])
    return _conn
