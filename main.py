import pandas as pd
import pandas_ta as ta
from binance.spot import Spot
from binance.error import ClientError
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch

PORCENTAJE_SL = 2
PORCENTAJE_TP = 8
MONTO_OPERACION = 0.0001
INTERVALO_POR_DEFECTO = "1h"

def obtener_datos(simbolo="BTCUSDT", intervalo=INTERVALO_POR_DEFECTO):
try:
velas = Spot().klines(simbolo, intervalo, limit=120)

    df = pd.DataFrame(velas, columns=[
        "tiempo", "apertura", "maximo", "minimo", "cierre", "volumen",
        "cierre_ts", "vol_cot", "trades", "vol_base",
        "vol_cot_total", "ignorar"
    ])

    cols = ["apertura", "maximo", "minimo", "cierre", "volumen"]
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")

    df["SMA20"] = ta.sma(df["cierre"], length=20)
    df["SMA50"] = ta.sma(df["cierre"], length=50)
    df["RSI"] = ta.rsi(df["cierre"], length=14)

    return df.dropna()

except Exception as e:
    print(f"Error: {e}")
    return None

def analizar(df):
u = df.iloc[-1]

precio = round(u["cierre"], 2)

sl = 0.0
tp = 0.0

if precio > u["SMA20"] and u["RSI"] < 35:
    señal = "🟢 COMPRAR SPOT"
    sl = round(precio * 0.98, 2)
    tp = round(precio * 1.08, 2)

elif precio < u["SMA20"] and u["RSI"] > 65:
    señal = "🔴 VENDER SPOT"
    sl = round(precio * 1.02, 2)
    tp = round(precio * 0.92, 2)

else:
    señal = "⚪ ESPERAR"

return {
    "senal": señal,
    "precio": precio,
    "rsi": round(u["RSI"], 2),
    "sma20": round(u["SMA20"], 2),
    "sl": sl,
    "tp": tp,
    "monto": MONTO_OPERACION
}

def operar_spot(simbolo, datos, api_key, api_secret, modo_real=False):

if not modo_real:
    return (
        f"✅ [SIMULACIÓN SPOT]\n"
        f"{datos['senal']}\n"
        f"Precio: {datos['precio']} | "
        f"SL: {datos['sl']} | TP: {datos['tp']}\n"
        f"Monto: {datos['monto']}\n"
        f"⚠️ No se envió orden real"
    )

try:
    cliente = Spot(
        api_key=api_key,
        api_secret=api_secret
    )

    if "COMPRAR" in datos["senal"]:

        cliente.new_order(
            symbol=simbolo,
            side="BUY",
            type="MARKET",
            quantity=datos["monto"]
        )

        return (
            f"✅ [REAL SPOT] COMPRA EJECUTADA\n"
            f"SL: {datos['sl']} | TP: {datos['tp']}"
        )

    elif "VENDER" in datos["senal"]:

        cliente.new_order(
            symbol=simbolo,
            side="SELL",
            type="MARKET",
            quantity=datos["monto"]
        )

        return "✅ [REAL SPOT] VENTA EJECUTADA"

    return "ℹ️ Sin señal"

except ClientError as e:
    return f"❌ Binance: {e.error_message}"

except Exception as e:
    return f"❌ Error: {str(e)}"

class Pantalla(BoxLayout):

def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.orientation = "vertical"
    self.padding = 12
    self.spacing = 10
    self.datos = None

    fila_api = BoxLayout(
        size_hint_y=0.1,
        spacing=10
    )

    self.input_key = TextInput(
        hint_text="API Key Binance",
        password=True,
        size_hint_x=0.5
    )

    self.input_secret = TextInput(
        hint_text="API Secret Binance",
        password=True,
        size_hint_x=0.5
    )

    fila_api.add_widget(self.input_key)
    fila_api.add_widget(self.input_secret)

    self.add_widget(fila_api)

    fila_modo = BoxLayout(
        size_hint_y=0.08,
        spacing=10
    )

    fila_modo.add_widget(
        Label(
            text="Simulación",
            size_hint_x=0.6
        )
    )

    self.switch_real = Switch(
        active=False,
        size_hint_x=0.15
    )

    fila_modo.add_widget(self.switch_real)

    fila_modo.add_widget(
        Label(
            text="Dinero Real",
            size_hint_x=0.25
        )
    )

    self.add_widget(fila_modo)

    fila_ctrl = BoxLayout(
        size_hint_y=0.1,
        spacing=10
    )

    self.simbolo = TextInput(
        text="BTCUSDT",
        size_hint_x=0.3
    )

    self.intervalo = Spinner(
        text=INTERVALO_POR_DEFECTO,
        values=["1m", "5m", "15m", "1h", "4h", "1d"],
        size_hint_x=0.3
    )

    fila_ctrl.add_widget(self.simbolo)
    fila_ctrl.add_widget(self.intervalo)

    fila_ctrl.add_widget(
        Button(
            text="CARGAR",
            on_press=self.cargar,
            size_hint_x=0.2
        )
    )

    fila_ctrl.add_widget(
        Button(
            text="OPERAR SPOT",
            on_press=self.ejecutar,
            size_hint_x=0.2
        )
    )

    self.add_widget(fila_ctrl)

    self.panel_grafico = Label(
        text="Gráfico deshabilitado para Android",
        size_hint_y=0.42
    )

    self.add_widget(self.panel_grafico)

    self.panel = Label(
        text="SparkTraderBot | Trading SPOT",
        size_hint_y=0.3
    )

    self.add_widget(self.panel)

def cargar(self, _):

    df = obtener_datos(
        self.simbolo.text.strip().upper(),
        self.intervalo.text
    )

    if df is None:
        self.panel.text = "❌ Error de conexión con Binance SPOT"
        return

    self.panel_grafico.text = (
        f"{self.simbolo.text.upper()} | "
        f"{self.intervalo.text}"
    )

    self.datos = analizar(df)

    d = self.datos

    modo = (
        "🔹 SIMULACIÓN"
        if not self.switch_real.active
        else "⚠️ REAL SPOT"
    )

    self.panel.text = (
        f"{modo}\n\n"
        f"📊 Precio: {d['precio']}\n"
        f"📈 RSI: {d['rsi']}\n"
        f"📉 SMA20: {d['sma20']}\n"
        f"🎯 {d['senal']}\n"
        f"⚠️ SL: {d['sl']} | TP: {d['tp']}\n"
        f"💰 Monto: {d['monto']}"
    )

def ejecutar(self, _):

    if not self.datos:
        self.panel.text += "\n\n❌ Primero carga los datos"
        return

    if (
        self.switch_real.active and
        (
            not self.input_key.text or
            not self.input_secret.text
        )
    ):
        self.panel.text += "\n\n❌ En modo REAL ingresa tus claves"
        return

    res = operar_spot(
        self.simbolo.text.strip().upper(),
        self.datos,
        self.input_key.text.strip(),
        self.input_secret.text.strip(),
        self.switch_real.active
    )

    self.panel.text += f"\n\n{res}"

class BotApp(App):
def build(self):
return Pantalla()

if name == "main":
BotApp().run()
