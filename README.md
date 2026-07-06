# 🚀 Spark-TraderBot
Bot de trading automatizado profesional para Binance Spot, con estrategia RSI + Stop-Loss / Take-Profit, gráficos en tiempo real y compilación APK para Android.

---

## ✨ Características Principales
- 🤖 **Estrategia**: RSI(14) en velas de 1h → Compra <30 | Vende >70
- 🛡️ **Gestión de Riesgo**: SL 2% / TP 8% → Relación riesgo/beneficio **1:4**
- 📊 **Interfaz**: Pestañas de control + gráfico de velas interactivo
- 📱 **APK Nativo**: Compilación automática vía GitHub Actions (modo release)
- 🔒 **Seguridad**: Claves en archivo `.env` — nunca expuestas ni incluidas en el APK
- ⚙️ **Testnet incluido**: Pruebas sin riesgo antes de operar con fondos reales
- 📈 **Par predeterminado**: **BTCUSDT** (el más líquido y estable)
- 💸 **Monto mínimo**: **0.0001 BTC** (~10.000 ARS) → ideal para capital reducido

---

## 📁 Estructura del Proyecto
<pre>
Spark-TraderBot/
├── 📂 assets/               # Iconos y pantalla de carga
│   ├── icon.png
│   └── splash.png
├── main.py                  # Lógica y interfaz completa
├── .env.example             # Plantilla de configuración segura
├── requirements.txt         # Dependencias optimizadas
├── buildozer.spec          # Configuración para APK
├── .gitignore              # Protege archivos sensibles
├── LICENSE                 # Licencia MIT
└── 📂 .github/workflows/
└── build-apk.yml       # Compilación automática
 </pre>

---

## 🔑 Configuración en Binance
1. Ir a **Perfil → Gestión de API → Crear API** → Nombre: `Spark-TraderBot`
2. **Permisos OBLIGATORIOS**:
   - ✅ Lectura de información
   - ✅ Trading Spot
   - ❌ **RETIROS DESACTIVADOS** (fundamental)
3. Guardar **API_KEY** y **API_SECRET** — solo se ven una vez
4. Recomendado: Usar **subcuenta** con saldo limitado

---

## 📱 Instalación y Conexión al APK
1. Descargar el APK desde **Actions → Artifacts**
2. Crear archivo `.env` en la misma carpeta del APK:
   ```env
   BINANCE_API_KEY=tu_clave_aqui
   BINANCE_SECRET_KEY=tu_secreto_aqui
   TESTNET=True  # Cambiar a False para operar real
3. Abrir app → Verificar conexión 🟢 → Listo para operar
 
 
 
⚙️ Parámetros Configurables en  main.py

  Python 
  
  SYMBOL = "BTCUSDT"                  # Cambiar por ETHUSDT, SOLUSDT, etc.
INTERVAL = Client.KLINE_INTERVAL_1HOUR  # Opciones: 30MINUTE, 4HOUR, 1DAY
CANTIDAD = 0.0001                   # Monto por operación
STOP_LOSS_PCT = 2.0                 # Pérdida máxima permitida
TAKE_PROFIT_PCT = 8.0               # Ganancia objetivo
 

 ## ⚠️ Aviso Importante
 
- El trading de criptomonedas implica riesgo de pérdida
- Probá primero en Testnet para validar todo sin riesgo
- Este software es una herramienta — no garantiza ganancias
- Nunca compartas tus claves API ni subas  .env  a GitHub
