from unittest.mock import MagicMock, patch
from src.agents.tools.stock import get_stock_price
from src.agents.tools.calculator import calculator

def test_stock_price_missing_market_cap():
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.info = {
        "longName": "Test Corp",
        "currentPrice": 150.0,
        "fiftyTwoWeekHigh": 180.0,
        "fiftyTwoWeekLow": 120.0,
        "marketCap": "N/A",  # Non-numeric / missing marketCap
        "sector": "Technology"
    }

    with patch("yfinance.Ticker", return_value=mock_ticker_instance):
        result = get_stock_price.invoke({"ticker": "TEST"})
        assert "Market Cap: N/A" in result
        assert "Price     : $150.0" in result

def test_calculator_tool():
    res = calculator.invoke({"expression": "10 + 20 * 2"})
    assert res == "50"

if __name__ == "__main__":
    test_stock_price_missing_market_cap()
    test_calculator_tool()
    print("All tool unit tests passed successfully!")
