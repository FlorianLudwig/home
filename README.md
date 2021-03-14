# Home automation

 * Change color of light depended on time of day

## todo

 deploy files from rp3

## deployment

### via ansible (raspberry pi3)

Create inventory and run
```
pipenv --python 3
pipenv install
pipenv run ansible-playbook -i inventory ansible-playbook.yml
```


## disable bluetooth for use of zigbee shield

```
dtoverlay=disable-bt
```

### locally via cli (On x64)

```
docker run --name=appdaemon -it -d --net=host \
  -e HA_URL="http://127.0.0.1:8123" \
  -e DASH_URL="http://0.0.0.0:5050" \
  -v /etc/app-daemon:/conf \
  -v /etc/localtime:/etc/localtime \
  test:latest

docker run -d --name="home-assistant" -v /etc/home-assistant:/config -v /etc/localtime:/etc/localtime:ro --net=host homeassistant/raspberrypi3-homeassistant:0.78.2

```


## Sources

```shell
wget https://raw.githubusercontent.com/dmulcahey/zha-network-card/master/zha-network-card.js

```


# Air Quality

How to interpretate values:

## Indoor CO2

 * https://iotfactory.eu/the-importance-of-indoor-air-quality-iaq-for-business-performance-and-wellbeing/
 * https://www.researchgate.net/figure/Description-of-Indoor-Air-Quality-on-the-basis-of-carbon-dioxide-concentration-10_tbl1_317135711