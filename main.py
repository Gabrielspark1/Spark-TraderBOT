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
from kivy.utils import platform

from binance.client import Client

# --- WEBVIEW NATIVO SIN GARDEN ---
# Intenta usar WebView nativo de Android, si no está en PC usa Label
NativeWebView = None
if platform == 'android':
    try:
        from jnius import autoclass, cast
        from android.runnable import run_on_ui_thread
        
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        WebSettings = autoclass('android.webkit.WebSettings')
        LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
        LinearLayout = autoclass('android.widget.LinearLayout')
        
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        
        class NativeWebView:
            def __init__(self, size_hint_y=0.35):
                self.size_hint_y = size_hint_y
                self.webview = None
                self._create_webview()
            
            @run_on_ui_thread
            def _create_webview(self):
                self.webview = WebView(activity)
                self.webview.getSettings().setJavaScriptEnabled(True)
                self.webview.getSettings().setDomStorageEnabled(True)
                self.webview.getSettings().setLoadWithOverviewMode(True)
                self.webview.getSettings().setUseWideViewPort(True)
                self.webview.setWebViewClient(WebViewClient())
                # Agregar al layout de Android
                activity.addContentView(self.webview, LayoutParams(LayoutParams.MATCH_PARENT, 600))
            
            @run_on_ui_thread
            def load_url(self, symbol="BTCUSDT", interval="60"):
                if not self.webview:
                    return
                # HTML TradingView igual al que tenías
                html = f"""
                <!DOCTYPE html>
                <html>
                <head><meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>html,body{{margin:0;padding:0;height:100%;background:#121212;}}</style></head>
                <body>
                <div id="tv" style="height:100vh;width:100vw"></div>
                <script src="https://s.tradingview.com/tv.js"></script>
                <script>
                new TradingView.widget({{
                    "autosize": true,
                    "symbol": "BINANCE:{symbol}",
                    "interval": "{interval}",
                    "timezone": "America/Argentina/Buenos_Aires",
                    "theme": "dark",
                    "style": "1",
                    "locale": "es",
                    "container_id": "tv"
                }});
                </script>
                </body>
                </html>
                """
                self.webview.loadDataWithBaseURL("https://tradingview.com", html, "text/html", "utf-8", None)
                
    except Exception as e:
        print(f"No se pudo crear WebView nativo: {e}")
        NativeWebView = None


# --- FUNCIONES PURE PYTHON ---
def calcular_rsi_pure(cierres, periodo=14):
    if len(cierres) < periodo + 1:
        return 50.0
    deltas = [cierres[i] - cierres[i-1] for i in range(1, len(cierres))]
    ganancias = [d if d > 0 else 0 for d in deltas]
    perdidas = [-d if d < 0 else 0 for d in deltas]
    avg_gan = sum(ganancias[:periodo]) / periodo
    avg_per = sum(perdidas[:periodo]) / periodo
    for i in range(periodo, len(ganancias)):
        avg_gan = (avg_gan * (periodo-1) + ganancias[i]) / periodo
        avg_per = (avg_per * (periodo-1) + perdidas[i]) / periodo
    if avg_per == 0:
        return 100.0
    rs = avg_gan / avg_per
    return round(100 - (100 / (1 + rs)), 2)

def calcular_sma_pure(cierres, periodo=20):
    if not cierres:
        return 0.0
    if len(cierres) < periodo:
        return round(sum(cierres) / len(cierres), 2)
    return round(sum(cierres[-periodo:]) / periodo, 2)


class SparkTraderBotUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 6

        self.cliente_binance = None
        self.modo_real = False
        self.moneda = "BTCUSDT"
        self.tiempo_grafico = "1h"
        self.monto_operacion = 0.0001
        self.trading_automatico = False
        self.evento_automatico = None
        self.posicion_abierta = False
        self.precio_compra_previo = 0.0
        self.STOP_LOSS_PCT = -2.0
        self.TAKE_PROFIT_PCT = 8.0

        self.dict_intervalos = {
            "1 Minuto": "1m",
            "5 Minutos": "5m",
            "15 Minutos": "15m",
            "1 Hora": "1h",
            "4 Horas": "4h"
        }
        self.tv_interval_map = {"1m":"1","5m":"5","15m":"15","1h":"60","4h":"240"}

        self.add_widget(Label(text="🤖 SparkTraderBot Advanced SL/TP", font_size=20, size_hint_y=None, height=35))

        # --- GRAFICO ---
        if platform == 'android' and NativeWebView:
            # WebView nativo Android sin garden
            self.webview_nativo = NativeWebView()
            self.add_widget(Label(text=f"📈 {self.moneda} - {self.tiempo_grafico} - TradingView", size_hint_y=None, height=25, color=(0.2,0.8,1,1)))
            # Cargar grafico después de 1 seg
            Clock.schedule_once(lambda dt: self.cargar_grafico_nativo(), 1)
        else:
            # En PC o si falla, Label informativo
            self.lbl_grafico = Label(
                text=f"📈 Grafico TradingView: {self.moneda} ({self.tiempo_grafico})\n[En Android se ve el grafico real]",
                size_hint_y=0.20,
                color=(0.2, 0.8, 1, 1)
            )
            self.add_widget(self.lbl_grafico)

        # --- PARAMETROS ---
        panel_parametros = GridLayout(cols=3, size_hint_y=None, height=40, spacing=4)
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

        # --- CONEXION ---
        panel_api = GridLayout(cols=3, size_hint_y=None, height=40, spacing=4)
        self.api_key = TextInput(hint_text="API Key", password=True, multiline=False)
        panel_api.add_widget(self.api_key)
        self.api_secret = TextInput(hint_text="Secret Key", password=True, multiline=False)
        panel_api.add_widget(self.api_secret)
        self.btn_conectar = Button(text="🔗 Conectar", background_color=(0.1, 0.5, 0.8, 1))
        self.btn_conectar.bind(on_press=self.conectar_binance)
        panel_api.add_widget(self.btn_conectar)
        self.add_widget(panel_api)

        # --- SWITCHES ---
        panel_switches = GridLayout(cols=4, size_hint_y=None, height=40, spacing=4)
        panel_switches.add_widget(Label(text="Real ⚠️", font_size=12))
        self.switch_modo = Switch(active=self.modo_real)
        self.switch_modo.bind(active=self.cambiar_modo_entorno)
        panel_switches.add_widget(self.switch_modo)
        panel_switches.add_widget(Label(text="Auto 🤖", font_size=12))
        self.switch_auto = Switch(active=self.trading_automatico, disabled=True)
        self.switch_auto.bind(active=self.controlar_bot_automatico)
        panel_switches.add_widget(self.switch_auto)
        self.add_widget(panel_switches)

        # --- TELEMETRIA ---
        self.lbl_rsi = Label(text="RSI: --- | SMA 20: --- | Precio: ---", size_hint_y=None, height=25, font_size=13)
        self.add_widget(self.lbl_rsi)
        self.lbl_senal = Label(text="Señal: ESPERAR", font_size=14, size_hint_y=None, height=25)
        self.add_widget(self.lbl_senal)

        self.add_widget(Label(text="📜 Historial (SL: -2% | TP: +8%)", font_size=13, size_hint_y=None, height=20))
        scroll_historial = ScrollView(size_hint_y=0.35)
        self.layout_historial = GridLayout(cols=1, size_hint_y=None, spacing=2)
        self.layout_historial.bind(minimum_height=self.layout_historial.setter('height'))
        scroll_historial.add_widget(self.layout_historial)
        self.add_widget(scroll_historial)

    def cargar_grafico_nativo(self):
        if hasattr(self, 'webview_nativo') and self.webview_nativo:
            tv_int = self.tv_interval_map.get(self.tiempo_grafico, "60")
            self.webview_nativo.load_url(self.moneda, tv_int)

    def actualizar_monto_dinamico(self, instancia, texto):
        try:
            valor = float(texto.strip())
            if valor > 0:
                self.monto_operacion = valor
        except:
            pass

    def cambiar_par_moneda(self, spinner, texto):
        self.moneda = texto
        if hasattr(self, 'lbl_grafico'):
            self.lbl_grafico.text = f"📈 {self.moneda} - {self.tiempo_grafico}"
        self.cargar_grafico_nativo()
        self.actualizar_analisis()

    def cambiar_intervalo_tiempo(self, spinner, texto):
        self.tiempo_grafico = self.dict_intervalos.get(texto, self.tiempo_grafico)
        if hasattr(self, 'lbl_grafico'):
            self.lbl_grafico.text = f"📈 {self.moneda} - {self.tiempo_grafico}"
        self.cargar_grafico_nativo()
        if self.trading_automatico:
            self.reiniciar_bucle_automatico()
        else:
            self.actualizar_analisis()

    def conectar_binance(self, instance):
        api_k = self.api_key.text.strip()
        api_s = self.api_secret.text.strip()
        if not api_k or not api_s:
            self.aviso("❌ Ingresa API Key y Secret")
            return
        try:
            self.cliente_binance = Client(api_k, api_s)
            if not self.modo_real:
                self.cliente_binance.API_URL = 'https://testnet.binance.vision/api'
            self.cliente_binance.get_account()
            self.switch_auto.disabled = False
            self.aviso("✅ Conectado\nModo: " + ("REAL" if self.modo_real else "TESTNET"))
            self.actualizar_analisis()
        except Exception as e:
            self.aviso(f"❌ Error:\n{str(e)[:200]}")

    def cambiar_modo_entorno(self, instancia, valor):
        self.modo_real = valor
        self.aviso("⚠️ REAL" if valor else "🧪 SIMULACIÓN")

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
        datos = self.obtener_datos_velas()
        if datos is None:
            return
        cierres = datos['cierres']
        senal = self.actualizar_analisis(datos)
        precio_actual = cierres[-1] if cierres else 0.0
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
            datos = self.obtener_datos_velas()
            precio_ejecucion = datos['cierres'][-1] if datos and datos['cierres'] else 0.0
            monto_actual = self.monto_operacion
            tipo_cuenta = "SIM"
            if self.modo_real and self.cliente_binance:
                try:
                    self.cliente_binance.create_order(symbol=self.moneda, side=lado, type='MARKET', quantity=monto_actual)
                    tipo_cuenta = "REAL"
                except Exception as e:
                    self.aviso(f"❌ Error orden real:\n{e}")
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

            lbl = Label(text=str_fila, size_hint_y=None, height=28, font_size=11, color=color_fila)
            lbl.bind(size=lambda *x: setattr(lbl, 'text_size', (lbl.width, None)))
            self.layout_historial.add_widget(lbl)
        except Exception as e:
            self.aviso(f"❌ Falló orden:\n{str(e)}")

    def obtener_datos_velas(self):
        if not self.cliente_binance:
            return None
        try:
            velas = self.cliente_binance.get_klines(symbol=self.moneda, interval=self.tiempo_grafico, limit=100)
            cierres = []
            for v in velas:
                try:
                    cierres.append(float(v[4]))
                except:
                    continue
            return {'cierres': cierres}
        except:
            return None

    def actualizar_analisis(self, datos_interno=None):
        datos = datos_interno if datos_interno is not None else self.obtener_datos_velas()
        if datos is None or not datos['cierres']:
            return None
        cierres = datos['cierres']
        rsi = calcular_rsi_pure(cierres, 14)
        sma20 = calcular_sma_pure(cierres, 20)
        precio_actual = cierres[-1]
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
        Popup(title="SparkTraderBot", content=Label(text=mensaje), size_hint=(0.85, 0.35)).open()


class SparkTraderBotApp(App):
    def build(self):
        return SparkTraderBotUI()

if __name__ == "__main__":
    SparkTraderBotApp().run()
