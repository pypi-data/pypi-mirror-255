# auto_duo

Automatically pass each duo push, no need to click on cellphone every time.

Try at: http://duo.jtc1246.com/

## Installation

`pip install auto_duo`

#### Dependencies

Please install nodejs (recommends 18.0.0, see [Nodejs-version](#nodejs-version) for detail) and npm first.

Then use 
``` bash
npm install crypto
npm install @aelfqueen/xmlhttprequest
```

## Usage

``` python
from auto_duo import start_server
start_server('./duo_data.json', 8080)
```
Then open http://{your_ip}:8080 in browser, and follows the instructions in webpage.

The data will be loaded from and stored into your specified file, if not exist will create a new one.

## How it works

Your QR code contains the activation code from duo, the server will use this code to communicate with duo server, and continuously check whether there is a push, and agree it automatically if there is.


## Nodejs-version

I only know the following facts:
- Can work with nodejs 18.0.0
- Cannot work with nodejs 12.x.x

I don't know anything else about this.

#### I recommend you to:

- Install nodejs 18.0.0 directly if you haven't installed nodejs.
- If you have nodejs try your own version first, if it doesn't work (show fail on webpage but your QR code is correct), install 18.0.0.

You are welcome to create an issue to tell me which version works or not.

#### How to install a specific nodejs version

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
```
Then exit termianl and relaunch it,
```bash
nvm install 18.0.0
nvm use 18.0.0
```

Then use `node -v` to check whether it is installed correctly.

## LICENSE

My JavaScript code is modified from Duochrome ( https://github.com/FreshSupaSulley/Duochrome ), which is MIT licensed.

Source code is in [Duochrome](Duochrome) directory, and my JS code is in [js](js) directory and [auto_duo/data.py](auto_duo/data.py) (base64 encoded).

Thanks the original authors for their contribution.
