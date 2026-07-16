[app]
title = SparkTraderBot
package.name = sparktraderbot
package.domain = io.sparktraderbot
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests, bin, venv, .git

orientation = portrait
fullscreen = 0

# ✅ TODAS LAS LIBRERÍAS INCLUIDAS: kivy + binance + pandas + webview
requirements = python3, kivy==2.2.1, python-binance==1.0.19, pandas==2.2.2, https://github.com/kivy-garden/kivy_garden.webview/archive/refs/heads/master.zip

garden_packages = kivy_garden.webview

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.minapi = 21
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.0
android.arch = arm64-v8a, armeabi-v7a

presplash.filename = %(source.dir)s/assets/Splash.png
icon.filename = %(source.dir)s/assets/icon.png
presplash_color = #121212

[buildozer]
log_level = 2
warn_on_root = 0
android_clean = True
