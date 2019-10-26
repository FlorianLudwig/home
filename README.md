# Home automation

## deployment

### via ansible (raspberry pi3)

Create inventory and run
```
pipenv --python 3
pipenv install
pipenv run ansible-playbook -i inventory ansible-playbook.yml
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
