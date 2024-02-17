from setuptools import setup, find_packages

setup(
    name='tradingview_websocket',
    version='0.2',
    packages=find_packages(),
    install_requires=['websocket-client'],
    author='Serdar ARIKAN',
    author_email='serdardarikan@gmail.com',
    description='This Python package provides a simple WebSocket client for connecting to the TradingView WebSocket API. It allows users to subscribe to real-time financial data streams and retrieve historical data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SerdarARIKAN/tradingview_websocket',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
