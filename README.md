# elena


## Intro

Los bots de "señales" no son la mejor estrategia a largo plazo. Se suele decir que [DCA](https://en.wikipedia.org/wiki/Dollar_cost_averaging)
da mejor resultado haciendo [HODL](https://en.wikipedia.org/wiki/Bitcoin#Term_%22HODL%22)

## Supuestos
- Lo único seguro con las cryptos es que varían mucho
- La variación diaria tiene un mínimo estable
- Una estrategia que parece viable es hacer compras y ventas con beneficios "pequeños" en los períodos ascendentes y esperar en los descendentes
- El reto es no quedar atrapado en una subida
- Para minimizar ese riesgo es mejor solo utilizar monedas en las que se tenga confianza y que no importe manentener
- La primera estrategia no utiliza _stop limit_


## Instlación de _v1

Ejemplo para una Raspberry Pi

- Requisitos de sistema en debian/ubuntu
  - ```` sudo apt-get install git python3-pip python3-venv python3-psutil build-essential python3-dev python3-wheel cython3 libffi-dev libxml2-dev  libssl-dev libevent-dev zlib1g-dev ````
- Crear usuario 
  - ```` sudo adduser elena ````
- Con el nuevo usario
  - Poner claves .ssh (es más fácil)
  - Configurar git, recomendado pero no necesario si no se haran commits
  - ````
    git config --global user.name "TU NOMBRE"
    git config --global user.email "TU MAIL"
    git config --global push.default simple
    ````
  - Descargar código 
    - ```` git clone git@github.com:Ciskam-Lab/elena.git ````
  - Ejecutar install.sh
  - Pruebas
    - En el directorio sample_bots he dejado uno de pruebas.
    - El código está probado teniendo los .json en el mismo directorio que el elena_v1.py.
    - Se lo puede probar pasándole un fichero como parámetro.
    - Para ejecutarlo siempre hay que activar el virtual env primero con
      - ```` source $HOME/venv/bin/activate ````
    - Luego se puede hacer un 
      - ```` python elena_v1.py fichero_bot.json ```` 
  - Cuando esteis listos para pronerlo en el cron podéis usar el install-cron.sh
  

## Canales de YouTube
- https://www.youtube.com/c/HealthyPockets
- https://www.youtube.com/c/CoinBureau

## Podcast
- https://open.spotify.com/episode/0REubw0OVlEEGWRHKnT8MB?si=B-_OVL8aTdGqnr25QGThoQ&context=spotify%3Ashow%3A6XmXYWqm1zByvMedjtaiN4&nd=1


## Otros bots
- https://github.com/DeviaVir/zenbot
- https://github.com/CyberPunkMetalHead/Binance-volatility-trading-bot


