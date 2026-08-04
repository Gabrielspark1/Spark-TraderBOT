[app]

title = Trader Bot
package.name = sparktraderbot
package.domain = io.github.gabrielspark1
version = 1.0.1

source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests,bin,venv,.git,.buildozer,.venv,__pycache__
source.main = main.py

orientation = portrait
fullscreen = 0

android.accept_sdk_license_agreement = True

# FINAL - SIN numpy/pandas/openssl/garden - CON pyjnius para WebView nativo
requirements = python3,kivy,pyjnius,requests,urllib3,certifi,charset-normalizer,idna,python-binance,pycryptodome,python-dateutil,android

p4a.whitelist = libffi,openssl,sqlite3
p4a.fork = kivy
p4a.branch = master
p4a.bootstrap = sdl2
p4a.port = 5000

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.minapi = 24
android.api = 33
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = False
android.ant = auto
android.enable_androidx = True

presplash.filename = %(source.dir)s/assets/Splash.png
icon.filename = %(source.dir)s/assets/icon.png
presplash.color = #121212

[buildozer]
log_level = 2
warn_on_root = 0
build_dir = ./.buildozer
bin_dir = ./bin
