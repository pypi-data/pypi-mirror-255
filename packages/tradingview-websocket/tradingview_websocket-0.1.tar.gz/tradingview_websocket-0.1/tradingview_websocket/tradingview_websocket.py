import json
import random
import re
import string
from websocket import create_connection

class TradingViewWebSocket:
    def __init__(self, symbol, timeframe, candles):
        self.ws = None
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = candles
        self.result_data = None

    def connect(self):
        headers = {
            'Connection': 'upgrade',
            'Host': 'data.tradingview.com',
            'Origin': 'https://data.tradingview.com',
            'Cache-Control': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Key': '1H41q97V8BbMKUq0knV1UA==',
            'Sec-WebSocket-Version': '13',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
            'Pragma': 'no-cache',
            'Upgrade': 'websocket'
        }
        self.ws = create_connection('wss://data.tradingview.com/socket.io/websocket', headers=headers)

    def generate_session(self):
        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        return "qs_" + random_string

    def generate_chart_session(self):
        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        return "cs_" + random_string

    def create_message(self, func, param_list):
        message = json.dumps({"m": func, "p": param_list}, separators=(',', ':'))
        return "~m~{}~m~{}".format(len(message), message)

    def send_message(self, func, args):
        message = self.create_message(func, args)
        self.ws.send(message)

    def run(self):
        session = self.generate_session()
        chart_session = self.generate_chart_session()
        symbol_string = "={\"symbol\":\"" + self.symbol + "\",\"adjustment\":\"splits\"}"

        self.send_message("set_auth_token", ["unauthorized_user_token"])
        self.send_message("chart_create_session", [chart_session, ""])
        self.send_message("quote_create_session", [session])
        self.send_message("quote_set_fields", [session, "ch", "chp", "current_session", "description", "local_description", "language", "exchange", "fractional", "is_tradable", "lp", "lp_time", "minmov", "minmove2", "original_name", "pricescale", "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
        self.send_message("quote_add_symbols", [session, self.symbol, {"flags": ['force_permission']}])
        self.send_message("resolve_symbol", [chart_session, "symbol_" + self.timeframe, symbol_string])
        self.send_message("create_series", [chart_session, "s" + self.timeframe, "s" + self.timeframe, "symbol_" + self.timeframe, self.timeframe, self.candles])

        while self.result_data is None:
            result = self.ws.recv()
            data = re.split('~m~\d+~m~', result)
            for i in data:
                try:
                    if i.strip():
                        parsed_data = json.loads(i)
                        if parsed_data.get('m') == 'timescale_update':
                            self.result_data = parsed_data['p'][1]['s' + str(self.timeframe)]['s']
                            return
                except Exception as e:
                    print("Error:", e)
                    continue
