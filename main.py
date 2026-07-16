from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.clock import Clock

# Librerías necesarias
from binance.client import Client
import pandas as pd
import numpy as np

class SparkTraderBotUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 30
        self.spacing = 12

        # Variables generales
        self.cliente_binance = None
        self.modo_real = False
        self.monto_operacion = 0.0001
        self.moneda = "BTCUSDT"
        self.tiempo_grafico = Client.KLINE_INTERVAL_1HOUR

        # --- TÍTULO ---
        self.add_widget(Label(text="🤖 SparkTraderBot", font_size=24, bold=True))

        # --- CONEXIÓN BINANCE ---
        self.add_widget(Label(text="🔑 Datos de conexión Binance", font_size=16))
        self.api_key = TextInput(hint_text="API Key", password=True, multiline=False)
        self.add_widget(self.api_key)
        self.api_secret = TextInput(hint_text="Secret Key", password=True, multiline=False)
        self.add_widget(self.api_secret)
        self.btn_conectar = Button(text="🔗 Conectar Binance", background_color=(0.1, 0.5, 0.8, 1))
        self.btn_conectar.bind(on_press=self.conectar_binance)
        self.add_widget(self.btn_conectar)

        # --- MODO SIMULACIÓN / REAL ---
        modo_layout = GridLayout(cols=2, size_hint_y=None, height=40)
        modo_layout.add_widget(Label(text="Modo Real (apagar = Simulación)"))
        self.switch_modo = Switch(active=self.modo_real)
        self.switch_modo.bind(active=self.cambiar_modo)
        modo_layout.add_widget(self.switch_modo)
        self.add_widget(modo_layout)

        # --- CAMBIAR MONTO ---
        self.add_widget(Label(text=f"💰 Monto por operación (BTC) | Actual: {self.monto_operacion}", font_size=15))
        self.input_monto = TextInput(
            hint_text="Ej: 0.0005 | 0.001",
            text=str(self.monto_operacion),
            multiline=False,
            input_filter="float"
        )
        self.add_widget(self.input_monto)
        self.btn_guardar_monto = Button(text="✅ Guardar monto", background_color=(0.2, 0.7, 0.3, 1))
        self.btn_guardar_monto.bind(on_press=self.actualizar_monto)
        self.add_widget(self.btn_guardar_monto)

        # --- INDICADORES CALCULADOS CON PANDAS ---
        self.add_widget(Label(text="📊 Indicadores en tiempo real", font_size=16, bold=True))
        self.lbl_rsi = Label(text="RSI (14): ---")
        self.add_widget(self.lbl_rsi)
        self.lbl_sma_corta = Label(text="SMA 20: ---")
        self.add_widget(self.lbl_sma_corta)
        self.lbl_sma_larga = Label(text="SMA 50: ---")
        self.add_widget(self.lbl_sma_larga)
        self.lbl_senal = Label(text="Señal: ---", font_size=15)
        self.add_widget(self.lbl_senal)

        # Botón para actualizar manualmente
        self.btn_actualizar = Button(text="🔄 Actualizar análisis", background_color=(0.8, 0.5, 0.1, 1))
        self.btn_actualizar.bind(on_press=self.actualizar_analisis)
        self.add_widget(self.btn_actualizar)

        # Actualiza automáticamente cada 5 minutos
        Clock.schedule_interval(lambda dt: self.actualizar_analisis(), 300)

    # --- Conexión Binance ---
    def conectar_binance(self, instancia):
        key = self.api_key.text.strip()
        secret = self.api_secret.text.strip()
        if not key or not secret:
            self.aviso("⚠️ Completa ambos campos de claves")
            return
        try:
            self.cliente_binance = Client(key, secret)
            self.cliente_binance.get_account()
            self.aviso("✅ Conectado correctamente")
            self.actualizar_analisis()
        except Exception as e:
            self.aviso(f"❌ Error:\n{str(e)}")

    # --- Cambiar modo ---
    def cambiar_modo(self, instancia, valor):
        self.modo_real = valor
        texto = "DINERO REAL ⚠️" if valor else "SIMULACIÓN ✅"
        self.aviso(f"Modo: {texto}")

    # --- Cambiar monto ---
    def actualizar_monto(self, instancia):
        try:
            nuevo = float(self.input_monto.text.strip())
            if nuevo <= 0: raise ValueError("Debe ser mayor a 0")
            self.monto_operacion = nuevo
            self.aviso(f"✅ Monto: {nuevo} BTC")
        except Exception as e:
            self.aviso(f"❌ Inválido: {str(e)}")

    # --- ✨ LÓGICA PANDAS: Obtener velas y calcular ---
    def obtener_datos_velas(self):
        if not self.cliente_binance:
            self.aviso("⚠️ Conecta primero a Binance")
            return None
        
        # Pedimos últimas 100 velas para cálculos exactos
        velas = self.cliente_binance.get_klines(
            symbol=self.moneda,
            interval=self.tiempo_grafico,
            limit=100
        )

        # Convertimos a tabla ordenada con Pandas
        df = pd.DataFrame(velas, columns=[
            'tiempo', 'apertura', 'maximo', 'minimo', 'cierre', 'volumen',
            'cierre_tiempo', 'volumen_total', 'operaciones', 'base_vol', 'coti_vol', 'ignorar'
        ])

        # Dejamos solo los valores numéricos que necesitamos
        df['cierre'] = pd.to_numeric(df['cierre'])
        return df

    # --- Cálculo RSI con Pandas ---
    def calcular_rsi(self, datos, periodo=14):
        delta = datos['cierre'].diff(1)
        ganancia = delta.where(delta > 0, 0)
        perdida = -delta.where(delta < 0, 0)

        media_ganancia = ganancia.rolling(window=periodo).mean()
        media_perdida = perdida.rolling(window=periodo).mean()

        rs = media_ganancia / media_perdida
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.iloc[-1], 2)

    # --- Análisis completo ---
    def actualizar_analisis(self, *args):
        df = self.obtener_datos_velas()
        if df is None: return

        # Calculamos todo con Pandas
        rsi = self.calcular_rsi(df)
        sma20 = round(df['cierre'].rolling(window=20).mean().iloc[-1], 2)
        sma50 = round(df['cierre'].rolling(window=50).mean().iloc[-1], 2)
        precio_actual = df['cierre'].iloc[-1]

        # Mostramos valores
        self.lbl_rsi.text = f"RSI (14): {rsi}"
        self.lbl_sma_corta.text = f"SMA 20: {sma20}"
        self.lbl_sma_larga.text = f"SMA 50: {sma50}"

        # Generamos señal simple
        if rsi < 30 and precio_actual > sma20:
            señal = "🟢 COMPRAR (RSI bajo + tendencia alcista)"
        elif rsi > 70 and precio_actual < sma20:
            señal = "🔴 VENDER (RSI alto + tendencia bajista)"
        else:
            señal = "⚪ ESPERAR"
        self.lbl_senal.text = f"Señal: {senal}"

    def aviso(self, mensaje):
        Popup(title="SparkTraderBot", content=Label(text=mensaje), size_hint=(0.85, 0.35)).open()

class SparkTraderBotApp(App):
    def build(self):
        return SparkTraderBotUI()

if __name__ == "__main__":
    SparkTraderBotApp().run()
