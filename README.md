# Random Words API  

Get Random Words with definition and pronunciation for Free using this API.  

## Requirements and Features 📑

- Python 3.8
- install Required Modules
- Fastapi: **<https://fastapi.tiangolo.com/>**
- Virtual Environment for Running FastAPI framework
- CORS Header and other Security Headers
- Swagger Docs Support
- Self-hosting support with gunicorn
- Support Nginx, Apache2, Lightspeed or Cloudflare Tunnel Proxy
- HTTPS (For Secure SSL Connections)  

## Setup and Development

```sh

## install python env
sudo apt install python3 python3-venv
pip install gunicorn

## Clone the Repo
git clone https://github.com/mskian/random-words-api
cd random-words-api

## Create Virtual Env
python3 -m venv venv

## Activate Virtual Env
source venv/bin/activate

## install Modules
pip install fastapi uvicorn httpx gunicorn

## start the dev server 
uvicorn app:app --host 0.0.0.0 --port 6021

## Exit virtual Env
deactivate
```

## Production Server

```sh
gunicorn -k uvicorn.workers.UvicornWorker app:app -b 0.0.0.0:6021 -w 2
```

## Systemd Conf

```sh
[Unit]
Description=Gunicorn instance to serve for Words API
Requires=network.target
After=network.target

[Service]
WorkingDirectory=/home/random-words-api
Environment="PATH=/home/random-words-api/venv/bin"
ExecStart=/home/random-words-api/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker app:app -b 0.0.0.0:6021 -w 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Usage

- `/` Home view

```json
{
  "status": "success",
  "api": "Random Words API",
  "version": "1.0.0",
  "total_words": 10009,
  "routes": {
    "home": "/",
    "random_word": "/random",
    "random_word_text": "/random?text=true",
    "word_by_id": "/word/{word_id}",
    "word_by_id_text": "/word/{word_id}?text=true",
    "full_data": "/data",
    "docs": "/docs"
  },
  "usage_examples": {
    "get_random": "/random",
    "get_random_text": "/random?text=true",
    "get_word_by_id": "/word/1",
    "get_word_by_id_text": "/word/1?text=true",
    "get_all_data": "/data"
  }
}
```

- `/random` - Random words data

```sh
http://localhost:6021/random
```

```json
{
  "status": "success",
  "data": {
    "id": 7037,
    "word": "Sanable",
    "definition": "Able to be healed",
    "pronunciation": "sanable"
  }
}
```

- `/word/1` - get word data by ID number

```sh
http://localhost:6020/word/1
```

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "word": "Palaeoclimatology",
    "definition": "Study of ancient climates",
    "pronunciation": "palaeoklimatoloj"
  }
}
```

- For more usage visit Swagger API Docs

```sh
http://localhost:6021/docs
```

## API Credits ☑

Get Random Words (with pronunciation) for Free using this API - <https://github.com/mcnaveen/Random-Words-API>  

## Disclaimer ⚠

We don't own any data or word. All belongs to the Respective owner of Website.
Using it for educational purpose only.  

## LICENSE

MIT
