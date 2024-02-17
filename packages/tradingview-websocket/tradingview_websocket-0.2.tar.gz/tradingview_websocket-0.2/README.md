# TradingView WebSocket Client

## Introduction
This Python package provides a simple WebSocket client for connecting to the TradingView WebSocket API. It allows users to subscribe to real-time financial data streams and retrieve historical data.

## Installation
You can install the package via pip:

```bash
pip install tradingview_websocket
```

## Usage

```python
from tradingview_websocket import TradingViewWebSocket
```

# Define symbol, timeframe, and number of candles
```python
symbol = "USDEUR"
timeframe = "1D"
candles = 100
```

# Initialize TradingViewWebSocket object
```python
ws = TradingViewWebSocket(symbol, timeframe, candles)
ws.connect()
```

# Run the WebSocket client
```python
ws.run()
```

# Access the result data
```python
result_data = ws.result_data
print(result_data)
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Issues
If you encounter any issues or have questions regarding the package, please feel free to open an issue on GitHub.
