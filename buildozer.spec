[app]

title = Trader Bot
package.name = sparktraderbot
package.domain = io.github.gabrielspark1
version = 1.0.1

source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests,bin,venv,.git,.buildozer,.venv

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True

requirements = python3,kivy==2.2.1,cython==0.29.33,numpy==1.23.5,pandas==1.5.3,requests,python-binance,openssl

garden_packages = webview

android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.minapi = 24
android.api = 33
android.ndk = 25b

android.archs = armeabi-v7a,arm64-v8a

presplash.filename = assets/Splash.png
icon.filename = assets/icon.png
presplash_color = #121212

[buildozer]

log_level = 2
warn_on_root = 0
android_clean = False
download_cache = .buildozer/cache
