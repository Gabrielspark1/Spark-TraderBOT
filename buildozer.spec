[app]
title = SparkTraderBot
package.name = sparktraderbot
package.domain = io.sparktraderbot
version = 1.0.1

source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests, bin, venv, .git

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True

# ✅ VERSIONES COINCIDENTES Y ESTABLES
requirements = python3, kivy==2.2.1, cython==0.29.33, numpy==1.23.5, pandas==2.0.3, python-binance==1.0.19, https://github.com/kivy-garden/kivy_garden.webview/archive/refs/heads/master.zip
garden_packages = kivy_garden.webview

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.minapi = 24
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.0
android.archs = arm64-v8a

presplash.filename = %(source.dir)s/assets/Splash.png
icon.filename = %(source.dir)s/assets/icon.png
presplash_color = #121212

[buildozer]
log_level = 2
warn_on_root = 0
android_clean = True
download_cache = .buildozer/cache
