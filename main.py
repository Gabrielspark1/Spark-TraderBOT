from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from kivy_garden.webview import WebView
from binance.client import Client
import pandas as pd
import numpy as np


class SparkTraderBotUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 6

        # --- Variables de Configuración ---
        self.cliente_binance = None
        self.modo_real = False
        self.moneda = "BTCUSDT"
        self.tiempo_grafico = "1h"
        self.monto_operacion = 0.0001

        # --- Estado del Bot ---
        self.trading_automatico = False
        self.evento_automatico = None
        self.posicion_abierta = False
        self.precio_compra_previo = 0.0

        # --- Configuración de Gestión de Riesgo ---
        self.STOP_LOSS_PCT = -2.0
        self.TAKE_PROFIT_PCT = 8.0

        self.dict_intervalos = {
            "1 Minuto": "1m",
            "5 Minutos": "5m",
            "15 Minutos": "15m",
            "1 Hora": "1h",
            "4 Horas": "4h"
        }

        # --- TÍTULO ---
        self.add_widget(Label(text="🤖 SparkTraderBot Advanced SL/TP", font_size=20, size_hint_y=None, height=30))

        # --- GRÁFICO DE VELAS (WEBVIEW) ---
        self.webview = WebView(size_hint_y=0.28)
        self.add_widget(self.webview)
        self.cargar_grafico_velas(self.moneda, self.tiempo_grafico)

        # --- PARÁMETROS DINÁMICOS DE OPERACIÓN ---
        panel_parametros = GridLayout(cols=3, size_hint_y=None, height=35, spacing=4)

        self.spin_moneda = Spinner(text="BTCUSDT", values=("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"))
        self.spin_moneda.bind(text=self.cambiar_par_moneda)
        panel_parametros.add_widget(self.spin_moneda)

        self.spin_intervalo = Spinner(text="1 Hora", values=tuple(self.dict_intervalos.keys()))
        self.spin_intervalo.bind(text=self.cambiar_intervalo_tiempo)
        panel_parametros.add_widget(self.spin_intervalo)

        self.input_monto = TextInput(text=str(self.monto_operacion), multiline=False, input_filter="float", hint_text="Monto")
        self.input_monto.bind(text=self.actualizar_monto_dinamico)
        panel_parametros.add_widget(self.input_monto)

        self.add_widget(panel_parametros)

        # --- CONEXIÓN BINANCE ---
        panel_api = GridLayout(cols=3, size_hint_y=None, height=35, spacing=4)
        self.api_key = TextInput(hint_text="API Key", password=True, multiline=False)
        panel_api.add_widget(self.api_key)
        self.api_secret = TextInput(hint_text="Secret Key", password=True, multiline=False)
        panel_api.add_widget(self.api_secret)
        self.btn_conectar = Button(text="🔗 Conectar", background_color=(0.1, 0.5, 0.8, 1))
        self.btn_conectar.bind(on_press=self.conectar_binance)
        panel_api.add_widget(self.btn_conectar)
        self.add_widget(panel_api)

        # --- INTERRUPTORES DE CONTROL ---
        panel_switches = GridLayout(cols=4, size_hint_y=None, height=35, spacing=4)
        panel_switches.add_widget(Label(text="Real ⚠️", font_size=12))
        self.switch_modo = Switch(active=self.modo_real)
        self.switch_modo.bind(active=self.cambiar_modo_entorno)
        panel_switches.add_widget(self.switch_modo)

        panel_switches.add_widget(Label(text="Auto 🤖", font_size=12))
        self.switch_auto = Switch(active=self.trading_automatico, disabled=True)
        self.switch_auto.bind(active=self.controlar_bot_automatico)
        panel_switches.add_widget(self.switch_auto)
        self.add_widget(panel_switches)

        # --- TELEMETRÍA ---
        self.lbl_rsi = Label(text="RSI: --- | SMA 20: --- | Precio: ---", size_hint_y=None, height=20, font_size=13)
        self.add_widget(self.lbl_rsi)
        self.lbl_senal = Label(text="Señal: ESPERAR", font_size=14, size_hint_y=None, height=20)
        self.add_widget(self.lbl_senal)

        # --- HISTORIAL VISIBLE ---
        self.add_widget(Label(text="📜 Historial de Órdenes Realizadas (SL: -2% | TP: +8%)", font_size=13, size_hint_y=None, height=20))

        scroll_historial = ScrollView(size_hint_y=0.25)
        self.layout_historial = GridLayout(cols=1, size_hint_y=None, spacing=2)
        self.layout_historial.bind(minimum_height=self.layout_historial.setter('height'))
        scroll_historial.add_widget(self.layout_historial)

        self.add_widget(scroll_historial)

    # --- Métodos de UI y lógica ---
    def actualizar_monto_dinamico(self, instancia, texto):
        try:
            valor = float(texto.strip())
            if valor > 0:
                self.monto_operacion = valor
        except Exception:
            pass

    def cambiar_par_moneda(self, spinner, texto):
        self.moneda = texto
        self.cargar_grafico_velas(self.moneda, self.tiempo_grafico)
        self.actualizar_analisis()

    def cambiar_intervalo_tiempo(self, spinner, texto):
        self.tiempo_grafico = self.dict_intervalos.get(texto, self.tiempo_grafico)
        self.cargar_grafico_velas(self.moneda, self.tiempo_grafico)
        if self.trading_automatico:
            self.reiniciar_bucle_automatico()
        else:
            self.actualizar_analisis()

    def cargar_grafico_velas(self, par_monedas, intervalo):
        tv_interval = "60"
        if "m" in intervalo:
            tv_interval = intervalo.replace("m", "")
        elif "h" in intervalo:
            try:
                tv_interval = str(int(intervalo.replace("h", "")) * 60)
            except Exception:
                tv_interval = "60"

        html_contenido = f"""
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>html, body {{ margin: 0; padding: 0; height: 100%; background-color: #121212; }}</style></head>
        <body>
            <div id="tradingview_chart" style="height:100vh;width:100vw"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
              "autosize": true, "symbol": "BINANCE:{par_monedas}", "interval": "{tv_interval}",
              "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "es",
              "hide_side_toolbar": true, "allow_symbol_change": false, "container_id": "tradingview_chart"
            }});
            </script>
        </body>
        </html>
        """
        try:
            self.webview.load_html(html_contenido)
        except Exception:
            # WebView embed failures shouldn't crash the app
            pass

    def conectar_binance(self, instancia):
        key = self.api_key.text.strip()
        secret = self.api_secret.text.strip()
        if not key or not secret:
            self.aviso("⚠️ Ingresa credenciales")
            return
        try:
            self.cliente_binance = Client(key, secret)
            # verificar credenciales mínimas
            _ = self.cliente_binance.get_account()
            self.switch_auto.disabled = False
            self.aviso("✅ Binance Conectado")
            self.actualizar_analisis()
        except Exception as e:
            self.aviso(f"❌ Error:\n{str(e)}")
            self.cliente_binance = None

    def cambiar_modo_entorno(self, instancia, valor):
        self.modo_real = valor
        self.aviso("⚠️ ENTORNO REAL" if valor else "🧪 MODO SIMULACIÓN")

    def controlar_bot_automatico(self, instancia, valor):
        self.trading_automatico = valor
        if valor:
            self.reiniciar_bucle_automatico()
        else:
            if self.evento_automatico:
                Clock.unschedule(self.evento_automatico)
                self.evento_automatico = None

    def reiniciar_bucle_automatico(self):
        if self.evento_automatico:
            Clock.unschedule(self.evento_automatico)
        self.evento_automatico = Clock.schedule_interval(lambda dt: self.ejecutar_ciclo_automatico(), 10)
        self.ejecutar_ciclo_automatico()

    def ejecutar_ciclo_automatico(self):
        df = self.obtener_datos_velas()
        if df is None:
            return

        senal = self.actualizar_analisis(df)
        precio_actual = df['cierre'].iloc[-1] if 'cierre' in df.columns and not df['cierre'].empty else 0.0

        if self.posicion_abierta and self.precio_compra_previo > 0:
            rendimiento_pct = ((precio_actual - self.precio_compra_previo) / self.precio_compra_previo) * 100

            if rendimiento_pct <= self.STOP_LOSS_PCT:
                self.ejecutar_orden_market("SELL", motivo=f"🚨 STOP LOSS ({round(rendimiento_pct, 2)}%)")
                return
            elif rendimiento_pct >= self.TAKE_PROFIT_PCT:
                self.ejecutar_orden_market("SELL", motivo=f"🎉 TAKE PROFIT (+{round(rendimiento_pct, 2)}%)")
                return

        if senal == "COMPRAR" and not self.posicion_abierta:
            self.ejecutar_orden_market("BUY", motivo="Indicadores 🟢")
        elif senal == "VENDER" and self.posicion_abierta:
            self.ejecutar_orden_market("SELL", motivo="Indicadores 🔴")

    def ejecutar_orden_market(self, lado, motivo=""):
        try:
            df = self.obtener_datos_velas()
            precio_ejecucion = df['cierre'].iloc[-1] if df is not None and 'cierre' in df.columns and not df['cierre'].empty else 0.0
            monto_actual = self.monto_operacion

            tipo_cuenta = "SIM"
            if self.modo_real and self.cliente_binance:
                try:
                    self.cliente_binance.create_order(
                        symbol=self.moneda,
                        side=lado,
                        type='MARKET',
                        quantity=monto_actual
                    )
                    tipo_cuenta = "REAL"
                except Exception as e:
                    self.aviso(f"❌ Error enviando orden real:\n{e}")
                    return

            pnl_texto = motivo
            if lado == "BUY":
                self.precio_compra_previo = precio_ejecucion
                self.posicion_abierta = True
            elif lado == "SELL":
                self.posicion_abierta = False
                if self.precio_compra_previo > 0:
                    pnl = ((precio_ejecucion - self.precio_compra_previo) / self.precio_compra_previo) * 100
                    pnl_texto = f"{motivo} | PnL: {'+' if pnl >= 0 else ''}{round(pnl, 2)}%"
                self.precio_compra_previo = 0.0

            str_fila = f"[{tipo_cuenta}] {lado} {monto_actual} {self.moneda} @ ${precio_ejecucion} | {pnl_texto}"

            color_fila = (0.9, 0.9, 0.9, 1)
            if "TAKE PROFIT" in pnl_texto or lado == "BUY":
                color_fila = (0.3, 1, 0.3, 1)
            elif "STOP LOSS" in pnl_texto:
                color_fila = (1, 0.3, 0.3, 1)

            lbl_registro = Label(text=str_fila, size_hint_y=None, height=25, font_size=11, color=color_fila)
            self.layout_historial.add_widget(lbl_registro)

        except Exception as e:
            self.aviso(f"❌ Falló orden:\n{str(e)}")

    def obtener_datos_velas(self):
        if not self.cliente_binance:
            return None
        try:
            velas = self.cliente_binance.get_klines(symbol=self.moneda, interval=self.tiempo_grafico, limit=100)
            df = pd.DataFrame(velas, columns=[
                'tiempo', 'apertura', 'maximo', 'minimo', 'cierre', 'volumen',
                'cierre_tiempo', 'volumen_total', 'operaciones', 'base_vol', 'coti_vol', 'ignorar'
            ])
            # convertir a numérico
            df['cierre'] = pd.to_numeric(df['cierre'], errors='coerce')
            df['apertura'] = pd.to_numeric(df['apertura'], errors='coerce')
            df['maximo'] = pd.to_numeric(df['maximo'], errors='coerce')
            df['minimo'] = pd.to_numeric(df['minimo'], errors='coerce')
            df.dropna(subset=['cierre'], inplace=True)
            return df
        except Exception:
            return None

    def calcular_rsi(self, datos, periodo=14):
        if datos is None or len(datos) < periodo + 1:
            return 50.0  # neutro si no hay datos suficientes
        delta = datos['cierre'].diff(1)
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=periodo, min_periods=periodo).mean()
        avg_loss = loss.rolling(window=periodo, min_periods=periodo).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        try:
            return round(float(rsi.iloc[-1]), 2)
        except Exception:
            return 50.0

    def actualizar_analisis(self, df_interno=None):
        df = df_interno if df_interno is not None else self.obtener_datos_velas()
        if df is None or df.empty:
            return None

        rsi = self.calcular_rsi(df)
        sma20 = round(df['cierre'].rolling(window=20, min_periods=1).mean().iloc[-1], 2)
        precio_actual = float(df['cierre'].iloc[-1])

        self.lbl_rsi.text = f"RSI: {rsi} | SMA 20: {sma20} | Precio: ${precio_actual}"

        if rsi < 30 and precio_actual > sma20:
            self.lbl_senal.text = "Señal: 🟢 COMPRAR"
            return "COMPRAR"
        elif rsi > 70 and precio_actual < sma20:
            self.lbl_senal.text = "Señal: 🔴 VENDER"
            return "VENDER"
        else:
            self.lbl_senal.text = "Señal: ⚪ ESPERAR"
            return "ESPERAR"

    def aviso(self, mensaje):
        Popup(title="SparkTraderBot Guard", content=Label(text=mensaje), size_hint=(0.85, 0.35)).open()


class SparkTraderBotApp(App):
    def build(self):
        return SparkTraderBotUI()


if __name__ == "__main__":
    SparkTraderBotApp().run()
