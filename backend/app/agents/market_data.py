from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.services.chat_data_service import ChatDataService
import yfinance as yf
import requests
from datetime import datetime
import time


class MarketDataAgent(BaseAgent):
    """
    Market Data Agent - Provides real-time market data for stocks, crypto, and currency exchange rates.
    """

    def __init__(self, data_service: ChatDataService):
        user_profile = data_service.get_user_profile()
        user_currency = user_profile.get('currency', 'SEK')

        # Create a session for yfinance to reuse connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        super().__init__(
            name="Market Data Specialist",
            role="Real-time Market Data Provider",
            instructions=f"""You are a market data specialist with access to real-time financial market information.

Your capabilities:
- Get current stock prices for any publicly traded company
- Get cryptocurrency prices (Bitcoin, Ethereum, etc.)
- Convert between currencies using current exchange rates
- Provide basic stock information (market cap, P/E ratio, 52-week high/low)

User's preferred currency: {user_currency}

Guidelines:
- Always provide current/real-time data when available
- Include the timestamp of the data
- Explain what the data means in simple terms
- If a stock symbol is ambiguous, clarify with the user
- For currency conversions, show the exchange rate used
- Round monetary values to 2 decimal places

Examples:
- "AAPL" or "Apple" → Get Apple Inc. stock price
- "BTC-USD" or "Bitcoin" → Get Bitcoin price in USD
- "Convert 1000 USD to SEK" → Get current exchange rate and convert

Important:
- Use the tools provided to fetch real-time data
- Don't make up or estimate prices - always use actual data
- If data is unavailable, clearly state that"""
        )
        self.data_service = data_service
        self.user_currency = user_currency

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define market data functions"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "description": "Get current stock price and information for a given ticker symbol",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL, TSLA, MSFT)"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_crypto_price",
                    "description": "Get current cryptocurrency price",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Crypto symbol (e.g., BTC-USD, ETH-USD)"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "convert_currency",
                    "description": "Convert amount from one currency to another using current exchange rates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "Amount to convert"
                            },
                            "from_currency": {
                                "type": "string",
                                "description": "Source currency code (e.g., USD, EUR, SEK)"
                            },
                            "to_currency": {
                                "type": "string",
                                "description": "Target currency code (e.g., USD, EUR, SEK)"
                            }
                        },
                        "required": ["amount", "from_currency", "to_currency"]
                    }
                }
            }
        ]

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute market data function"""
        if function_name == "get_stock_price":
            return self._get_stock_price(arguments["symbol"])
        elif function_name == "get_crypto_price":
            return self._get_crypto_price(arguments["symbol"])
        elif function_name == "convert_currency":
            return self._convert_currency(
                arguments["amount"],
                arguments["from_currency"],
                arguments["to_currency"]
            )
        else:
            return {"error": f"Unknown function: {function_name}"}

    def _get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price using yfinance with session and retry logic"""
        try:
            # Use session for better connection handling
            stock = yf.Ticker(symbol.upper(), session=self.session)

            # Add small delay to avoid rate limiting
            time.sleep(0.5)

            # Try history first (most reliable method)
            try:
                hist = stock.history(period="5d")  # Get last 5 days
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]

                    # Try to get additional info, but don't fail if unavailable
                    try:
                        info = stock.info
                        name = info.get('longName', info.get('shortName', symbol))
                        currency = info.get('currency', 'USD')
                        market_cap = info.get('marketCap')
                        pe_ratio = info.get('trailingPE')
                        week_52_high = info.get('fiftyTwoWeekHigh')
                        week_52_low = info.get('fiftyTwoWeekLow')
                    except:
                        # If info fails, use basic data from history
                        name = symbol.upper()
                        currency = 'USD'
                        market_cap = None
                        pe_ratio = None
                        week_52_high = hist['High'].max()
                        week_52_low = hist['Low'].min()

                    result = {
                        "symbol": symbol.upper(),
                        "name": name,
                        "current_price": round(float(current_price), 2),
                        "currency": currency,
                        "market_cap": market_cap,
                        "pe_ratio": pe_ratio,
                        "52_week_high": week_52_high,
                        "52_week_low": week_52_low,
                        "timestamp": datetime.now().isoformat(),
                        "date": hist.index[-1].strftime("%Y-%m-%d")
                    }
                    return result
            except Exception as hist_error:
                print(f"History method failed: {hist_error}")

            # Fallback: Try fast_info
            try:
                time.sleep(0.5)
                fast_info = stock.fast_info
                current_price = fast_info.get('lastPrice') or fast_info.get('regularMarketPrice')
                if current_price:
                    return {
                        "symbol": symbol.upper(),
                        "name": symbol.upper(),
                        "current_price": round(float(current_price), 2),
                        "currency": fast_info.get('currency', 'USD'),
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as fast_error:
                print(f"Fast info method failed: {fast_error}")

            return {
                "error": f"Unable to fetch price for {symbol}. This could be due to:\n" +
                        "- Temporary API rate limiting (please try again in a moment)\n" +
                        "- Invalid ticker symbol\n" +
                        "- Market is closed\n" +
                        "- Stock is delisted or suspended"
            }

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                return {
                    "error": f"Rate limit exceeded for {symbol}. Please wait a moment and try again. " +
                            "Yahoo Finance has temporary request limits."
                }
            return {"error": f"Error fetching stock data for {symbol}: {error_msg}"}

    def _get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """Get cryptocurrency price using yfinance with session"""
        try:
            # Ensure symbol ends with -USD if not specified
            if '-' not in symbol:
                symbol = f"{symbol.upper()}-USD"

            crypto = yf.Ticker(symbol, session=self.session)
            time.sleep(0.5)

            # Try history first (most reliable)
            try:
                hist = crypto.history(period="5d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]

                    try:
                        info = crypto.info
                        name = info.get('name', symbol)
                        change_percent = info.get('regularMarketChangePercent')
                        market_cap = info.get('marketCap')
                    except:
                        name = symbol
                        change_percent = None
                        market_cap = None

                    result = {
                        "symbol": symbol.upper(),
                        "name": name,
                        "current_price": round(float(current_price), 2),
                        "currency": "USD",
                        "24h_change_percent": change_percent,
                        "market_cap": market_cap,
                        "timestamp": datetime.now().isoformat(),
                        "date": hist.index[-1].strftime("%Y-%m-%d")
                    }
                    return result
            except Exception as hist_error:
                print(f"Crypto history failed: {hist_error}")

            return {
                "error": f"Unable to fetch crypto price for {symbol}. This could be due to:\n" +
                        "- Temporary API rate limiting\n" +
                        "- Invalid crypto symbol (try BTC-USD, ETH-USD, etc.)"
            }

        except Exception as e:
            if "429" in str(e):
                return {"error": f"Rate limit exceeded. Please wait a moment and try again."}
            return {"error": f"Error fetching crypto data for {symbol}: {str(e)}"}

    def _convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Convert currency using yfinance forex data"""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()

            if from_currency == to_currency:
                return {
                    "amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "converted_amount": amount,
                    "exchange_rate": 1.0,
                    "timestamp": datetime.now().isoformat()
                }

            # Use forex pair (e.g., USDSEK=X for USD to SEK)
            forex_symbol = f"{from_currency}{to_currency}=X"
            ticker = yf.Ticker(forex_symbol, session=self.session)
            time.sleep(0.5)

            # Try history first
            try:
                hist = ticker.history(period="5d")
                if not hist.empty:
                    exchange_rate = hist['Close'].iloc[-1]
                    converted_amount = amount * float(exchange_rate)

                    return {
                        "amount": round(amount, 2),
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "converted_amount": round(converted_amount, 2),
                        "exchange_rate": round(float(exchange_rate), 4),
                        "timestamp": datetime.now().isoformat(),
                        "date": hist.index[-1].strftime("%Y-%m-%d")
                    }
            except:
                pass

            # Try inverse pair
            forex_symbol = f"{to_currency}{from_currency}=X"
            ticker = yf.Ticker(forex_symbol, session=self.session)
            time.sleep(0.5)

            try:
                hist = ticker.history(period="5d")
                if not hist.empty:
                    inverse_rate = hist['Close'].iloc[-1]
                    exchange_rate = 1 / float(inverse_rate)
                    converted_amount = amount * exchange_rate

                    return {
                        "amount": round(amount, 2),
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "converted_amount": round(converted_amount, 2),
                        "exchange_rate": round(exchange_rate, 4),
                        "timestamp": datetime.now().isoformat(),
                        "date": hist.index[-1].strftime("%Y-%m-%d")
                    }
            except:
                pass

            return {
                "error": f"Could not find exchange rate for {from_currency} to {to_currency}. " +
                        "Please verify both currency codes are valid (e.g., USD, EUR, SEK)."
            }

        except Exception as e:
            if "429" in str(e):
                return {"error": "Rate limit exceeded. Please wait a moment and try again."}
            return {"error": f"Error converting currency: {str(e)}"}
