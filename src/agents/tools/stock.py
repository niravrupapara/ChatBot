import yfinance as yf
from langchain_core.tools import tool
from src.utils.logger import get_logger

logger = get_logger(__name__)


@tool
def get_stock_price(ticker: str) -> str:
    """Get current stock price and basic info for a ticker symbol. Example: 'AAPL', 'TSLA', 'GOOGL'"""
    logger.info(f"Stock price request for ticker: {ticker}")

    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if not price:
            return f"Could not find price for ticker '{ticker}'."

        market_cap = info.get("marketCap")
        market_cap_str = f"${market_cap:,}" if isinstance(market_cap, (int, float)) else "N/A"

        result = (
            f"Stock info for {info.get('longName', ticker.upper())} ({ticker.upper()}):\n"
            f"  Price     : ${price}\n"
            f"  52W High  : ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"  52W Low   : ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
            f"  Market Cap: {market_cap_str}\n"
            f"  Sector    : {info.get('sector', 'N/A')}"
        )
        logger.info(f"Stock data fetched for {ticker.upper()}")
        return result

    except Exception as e:
        logger.error(f"Stock fetch error for {ticker}: {e}")
        return f"Could not fetch stock data for '{ticker}': {e}"
