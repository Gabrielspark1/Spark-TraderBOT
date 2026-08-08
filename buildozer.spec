[app]
title = Trader Bot
package.name = sparktraderbot
package.domain = io.github.gabrielspark1
version = 1.0.1
source.dir =.
source.include_exts = py,png,jpg,kv,json,ttf
source.exclude_dirs = tests,bin,venv,.git,.buildozer,.venv,__pycache__
source.main = main.py
orientation = portrait
fullscreen = 0

p4a.bootstrap = sdl2
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.minapi = 24
android.api = 33
android.sdk = 33
android.ndk = 25b
android.archs = armeabi-v7a, arm64-v8a
android.allow_backup = False
android.accept_sdk_license_agreement = True
android.enable_androidx = True
requirements = python3,kivy,pyjnius,openssl,requests,python-binance,pycryptodome,python-dateutil
android.gradle_dependencies = androidx.core:core:1.9.0

presplash.filename = %(source.dir)s/assets/Splash.png
icon.filename = %(source.dir)s/assets/icon.png
presplash.color = #0F172A

[buildozer]
log_level = 2
warn_on_root = 0
