import unittest
from unittest.mock import MagicMock, patch
from tradingview_websocket import TradingViewWebSocket

class TestTradingViewWebSocket(unittest.TestCase):

    def test_run(self):
        # Dummy data
        symbol = "USDEUR"
        timeframe = "1D"
        candles = 100

        # Mock create_connection function
        with patch('tradingview_websocket_.create_connection') as mock_create_connection:
            mock_ws = MagicMock()
            mock_create_connection.return_value = mock_ws

            # Initialize TradingViewWebSocket object
            ws = TradingViewWebSocket(symbol, timeframe, candles)
            ws.connect()

            # Mock send_message function
            ws.send_message = MagicMock()

            # Run the websocket
            ws.run()

            # Check if send_message called with expected parameters
            ws.send_message.assert_called_with("set_auth_token", ["unauthorized_user_token"])
            ws.send_message.assert_called_with("chart_create_session", ["cs_RANDOM"])
            ws.send_message.assert_called_with("quote_create_session", ["qs_RANDOM"])
            ws.send_message.assert_called_with("quote_set_fields", ["qs_RANDOM", "ch", "chp", "current_session", "description", "local_description", "language", "exchange", "fractional", "is_tradable", "lp", "lp_time", "minmov", "minmove2", "original_name", "pricescale", "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
            ws.send_message.assert_called_with("quote_add_symbols", ["qs_RANDOM", "TEST", {"flags": ['force_permission']}])
            ws.send_message.assert_called_with("resolve_symbol", ["cs_RANDOM", "symbol_1D", "={\"symbol\":\"TEST\",\"adjustment\":\"splits\"}"])
            ws.send_message.assert_called_with("create_series", ["cs_RANDOM", "s1D", "s1D", "symbol_1D", "1D", 100])


if __name__ == '__main__':
    unittest.main()
