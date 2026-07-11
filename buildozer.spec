[app]
title = SparkTraderBot
package.name = sparktraderbot
package.domain = org.sparktraderbot

source.dir = .
source.include_exts = py,png,jpg,json
source.include_patterns = assets/*

version = 1.0.0

requirements = python3,
kivy,
matplotlib,
numpy,
pandas,
pandas-ta==0.3.14b0,
python-binance

android.minapi = 21
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.2

android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.apptheme = @android:style/Theme.Material.Light.NoActionBar

android.gradle_dependencies = com.android.volley:volley:1.2.1

android.icon = %(source.dir)s/assets/icon.png

presplash.filename = %(source.dir)s/assets/Splash.png
android.presplash_color = #121212

android.release_artifact = apk

android.archs = arm64-v8a,armeabi-v7a

log_level = 2
fullscreen = 0
orientation = portrait
