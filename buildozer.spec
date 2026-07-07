[app]
title = SparkTraderBot
package.name = sparktraderbot
package.domain = org.sparktraderbot
source.dir = .
source.include_exts = py,png,jpg,json
source.include_patterns = assets/*
version = 1.0.0

# ✅ REQUISITOS EXACTOS
requirements = python3==3.10,\
kivy==2.2.1,\
kivy_garden.webview==0.2.0,\
numpy==1.26.4,\
pandas==2.2.2,\
pandas-ta==0.3.14b0,\
plotly==5.20.0,\
binance-connector-python==3.0.2,\
requests==2.31.0

android.minapi = 21
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.2
android.sdk = 24
android.ndk_api = 21

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.apptheme = @android:style/Theme.Material.Light.NoActionBar
android.gradle_dependencies = com.android.volley:volley:1.2.1
android.icon = assets/logo.png

android.release_artifact = apk
log_level = 2
android.arch = arm64-v8a,armeabi-v7a
