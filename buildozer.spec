[app]
# App identity
title = Trader Bot
package.name = sparktraderbot
# Use a domain you control. If you don't have one, io.github/<username> is commonly used.
package.domain = io.github.Gabrielspark1
version = 1.0.1

# Source files
source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests, bin, venv, .git, .buildozer, .venv

# UI
orientation = portrait
fullscreen = 0

# Android / SDK
android.accept_sdk_license = True

# ===== Requirements =====
# Note: numpy and pandas are large and can cause build failures / big APKs.
# Consider moving heavy processing to a server or confirm p4a recipes for these versions.
requirements = python3, kivy==2.2.1, cython==0.29.33, numpy==1.23.5, pandas==2.0.3, requests, python-binance==1.0.19, openssl

# If you need a GitHub package, use pip's git format, e.g.:
# git+https://github.com/owner/repo.git@branch#egg=packagename
# example (uncomment if you actually need it):
# requirements += ,git+https://github.com/kivy-garden/garden.webview.git@master#egg=kivy_garden.webview

# Kivy garden packages — use the garden name here (or include the pip name in requirements)
garden_packages = webview

# Android permissions & SDK settings
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.minapi = 24
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.0
android.archs = armeabi-v7a, arm64-v8a

# Assets
presplash.filename = assets/Splash.png
icon.filename = assets/icon.png
presplash_color = #121212

[buildozer]
log_level = 2
warn_on_root = 0
android_clean = True
download_cache = .buildozer/cache

# Pin python-for-android branch for reproducible builds (optional)
# p4a.branch = master
