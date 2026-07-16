[app]
title = SparkTraderBot
package.name = sparktraderbot
package.domain = io.sparktraderbot
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,json,env
source.exclude_dirs = tests, bin, venv, .git

orientation = portrait
fullscreen = 0

# 🎯 REQUISITOS CLAVE PARA COMPILAR
# Opción 1: La que funciona 100% (descarga directa del repo oficial)
requirements = python3, kivy==2.2.1, https://github.com/kivy-garden/kivy_garden.webview/archive/refs/heads/master.zip

# 📌 Si prefieres versión mantenida sin garden:
# requirements = python3, kivy==2.2.1, kivywebview==0.3.0

# OBLIGATORIO si usas la opción 1:
garden_packages = kivy_garden.webview

# Permisos para Binance y conexión
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Configuración Android estable
android.minapi = 21
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.0
android.arch = arm64-v8a, armeabi-v7a

# Recursos visuales
presplash.filename = %(source.dir)s/assets/Splash.png
icon.filename = %(source.dir)s/assets/icon.png
presplash_color = #121212

[buildozer]
log_level = 2
warn_on_root = 0
android_clean = True
