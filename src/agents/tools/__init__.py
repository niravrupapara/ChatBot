from src.agents.tools.search import web_search
from src.agents.tools.calculator import calculator
from src.agents.tools.stock import get_stock_price
from src.agents.tools.rag_search import rag_search

ALL_TOOLS = [web_search, calculator, get_stock_price, rag_search]
