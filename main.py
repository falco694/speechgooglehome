import logging
import socket
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, request
from slugify import slugify

import pychromecast
import speech_gtts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chromecast_name = "home"  # edit me to be your google home group
private_ip = "{private IP}"

app = Flask(__name__)
logging.info("Starting up chromecasts")
chromecasts = pychromecast.get_chromecasts()
print(chromecasts)
cast = next(cc for cc in chromecasts if cc.device.friendly_name ==
            chromecast_name)


def play_tts(text, lang='en', slow=False):
    tts = speech_gtts.main(text)
    filename = "output.mp3"
    path = "/static/cache/"
    cache_filename = "." + path + filename
    tts_file = Path(cache_filename)
    if not tts_file.is_file():
        logging.info(tts)
        tts.save(cache_filename)

    urlparts = urlparse(request.url)
    mp3_url = "http://" + private_ip + path + filename
    logging.info(mp3_url)
    play_mp3(mp3_url)


def play_mp3(mp3_url):
    print(mp3_url)
    cast.wait()
    mc = cast.media_controller
    mc.play_media(mp3_url, 'audio/mp3')


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/play/<filename>')
def play(filename):
    urlparts = urlparse(request.url)
    mp3 = Path("./static/"+filename)
    if mp3.is_file():
        play_mp3("http://"+private_ip + ":5000/static/"+filename)
        return filename
    else:
        return "False"


@app.route('/say/')
def say():
    text = request.args.get("text")
    lang = request.args.get("lang")
    if not text:
        return False
    if not lang:
        lang = "ja"
    play_tts(text=text, lang=lang)
    return text


if __name__ == '__main__':
    app.run(debug=False, host=private_ip)
