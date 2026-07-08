[app]
title = SparkTraderBot
package.name = sparktraderbot
package.domain = org.sparktraderbot
source.dir = .
source.include_exts = py,png,jpg,json
source.include_patterns = assets/*
version = 1.0.0

# Requisitos limpios de espacios con las versiones estables para Android
requirements = python3,kivy,kivy_garden.webview,numpy==1.25.2,pandas==1.5.3,pandas-ta==0.3.14b0,plotly,binance-connector==3.0.2,requests,urllib3,certifi,six
 
# Configuración de plataforma de destino
android.minapi = 21
android.api = 33
android.ndk = 25b
android.buildtools = 33.0.2

# Permisos de red requeridos para el Bot de trading
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.apptheme = @android:style/Theme.Material.Light.NoActionBar
android.gradle_dependencies = com.android.volley:volley:1.2.1

# Direcciones de recursos visuales locales
android.icon = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/Splash.png
android.presplash_color = #121212

# Opciones de compilación final
android.release_artifact = apk
log_level = 2
android.arch = arm64-v8a
