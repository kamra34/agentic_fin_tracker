from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.services.chat_data_service import ChatDataService
import requests
from bs4 import BeautifulSoup
import json


class FinancialInformationAgent(BaseAgent):
    """
    Financial Information Agent - Provides general financial knowledge and comparisons
    using web search capabilities.
    """

    def __init__(self, data_service: ChatDataService):
        user_profile = data_service.get_user_profile()
        user_currency = user_profile.get('currency', 'SEK')
        user_country = 'Sweden' if user_currency == 'SEK' else 'International'

        super().__init__(
            name="Financial Information Specialist",
            role="General Financial Knowledge and Comparison Expert",
            instructions=f"""You are a financial information specialist with expertise in:
- Comparing banks and investment platforms
- Explaining financial products (savings accounts, ISK, KF, investment funds)
- Providing current interest rates and fees
- Swedish financial market knowledge (Avanza, Nordea, Nordnet, SEB, Handelsbanken, etc.)
- Investment strategies and account types
- Tax implications and regulations

User context:
- Preferred currency: {user_currency}
- Country focus: {user_country}

Your capabilities:
- Search the web for current financial information
- Compare different financial institutions
- Explain complex financial concepts in simple terms
- Provide unbiased, factual comparisons
- Stay up-to-date with current rates and offerings

Guidelines:
- Always search for the most current information
- Provide balanced, unbiased comparisons
- Cite where the information comes from when possible
- If information is outdated or unavailable, clearly state that
- Focus on Swedish institutions when the user currency is SEK
- Explain financial terms in simple language
- Consider fees, interest rates, accessibility, and features in comparisons

Swedish financial terminology:
- ISK (Investeringssparkonto) = Investment Savings Account
- KF (Kapitalförsäkring) = Capital Insurance
- Aktiesparfond = Equity fund
- Ränta = Interest rate
- Avgift = Fee

Important:
- Use web search to get current, accurate information
- Don't make assumptions about rates or fees - search for them
- Provide multiple perspectives when comparing options"""
        )
        self.data_service = data_service
        self.user_currency = user_currency

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define financial information functions"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_financial_info",
                    "description": "Search the web for current financial information, rates, comparisons, or general knowledge",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for financial information (e.g., 'Avanza interest rate 2024', 'Compare Nordea and SEB savings accounts')"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_institutions",
                    "description": "Compare specific financial institutions or products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "institution1": {
                                "type": "string",
                                "description": "First institution or product to compare"
                            },
                            "institution2": {
                                "type": "string",
                                "description": "Second institution or product to compare"
                            },
                            "comparison_type": {
                                "type": "string",
                                "description": "What to compare (e.g., 'savings account', 'ISK', 'fees', 'investment platform')"
                            }
                        },
                        "required": ["institution1", "institution2", "comparison_type"]
                    }
                }
            }
        ]

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute financial information function"""
        if function_name == "search_financial_info":
            return self._search_financial_info(arguments["query"])
        elif function_name == "compare_institutions":
            return self._compare_institutions(
                arguments["institution1"],
                arguments["institution2"],
                arguments["comparison_type"]
            )
        else:
            return {"error": f"Unknown function: {function_name}"}

    def _search_financial_info(self, query: str) -> Dict[str, Any]:
        """
        Provide structured guidance for financial information searches.
        Returns helpful information and sources based on the query.
        """
        try:
            from datetime import datetime
            current_year = datetime.now().year
            current_month = datetime.now().strftime("%B %Y")

            query_lower = query.lower()

            # Build a knowledge base response based on the query
            result = {
                "query": query,
                "type": "information_guidance",
                "current_period": current_month
            }

            # Swedish banks interest rates
            if any(word in query_lower for word in ['interest', 'ränta', 'rate', 'savings']):
                if any(bank in query_lower for bank in ['swedbank', 'handelsbanken', 'seb', 'nordea']):
                    result["information"] = f"""
**Checking Current Swedish Bank Interest Rates ({current_year})**

To find current savings account interest rates for Swedish banks:

**Official Bank Websites:**
- Swedbank: swedbank.se/privat/spara/sparkonton
- Handelsbanken: handelsbanken.se/sv/privat/spara-och-placera
- SEB: seb.se/privat/spara/sparkonto
- Nordea: nordea.se/privat/vara-produkter/spara.html

**Comparison Sites:**
- Compricer.se - Independent comparison of Swedish savings accounts
- Konsumenternas.se - Swedish Consumer Agency comparisons
- Ratsit.se - Financial product comparisons

**Important Notes:**
- Interest rates change frequently, often monthly
- Promotional rates may apply for new customers
- Check for minimum deposit requirements
- Verify if rate is guaranteed or variable
                    """
                    result["recommendation"] = "Visit the official bank websites above for the most accurate, up-to-date interest rates."
                    return result

            # Bank/platform comparisons
            if any(word in query_lower for word in ['compare', 'vs', 'versus', 'better', 'best']):
                institutions = []
                if 'avanza' in query_lower:
                    institutions.append('Avanza')
                if 'nordnet' in query_lower:
                    institutions.append('Nordnet')
                if any(bank in query_lower for bank in ['swedbank', 'nordea', 'seb', 'handelsbanken']):
                    institutions.append('Traditional banks')

                if institutions:
                    result["information"] = f"""
**Comparing {' vs '.join(institutions)}**

**Key Factors to Compare:**

**Investment Platforms (Avanza/Nordnet):**
- Trading fees (courtage): Typically 0.04-0.25% per trade
- ISK (Investment Savings Account) fees: Usually free or low annual fee
- Available markets: Swedish, Nordic, US, European stocks
- Fund selection: 1000+ funds available
- Research tools and analysis features
- Mobile app functionality

**Traditional Banks:**
- Higher fees generally
- Personal advisory services available
- Integrated with other banking services
- Physical branch access
- More conservative investment options

**Where to Compare:**
- Avanza.se - Sweden's largest online broker
- Nordnet.se - Popular Nordic investment platform
- Rikatillsammans.se - Swedish investment forum with comparisons
- Compricer.se - Independent comparison site
                    """
                    result["recommendation"] = f"For detailed comparison of fees and services, visit each platform's website and check independent reviews on Swedish financial forums."
                    return result

            # ISK/KF accounts
            if any(term in query_lower for term in ['isk', 'investeringssparkonto', 'kapitalförsäkring', 'kf']):
                result["information"] = """
**Swedish Investment Account Types (ISK & KF)**

**ISK (Investeringssparkonto) - Investment Savings Account:**
- Flat tax rate (~1.2% of account value per year, based on government interest rate)
- No tax on actual profits or dividends
- Best for active trading or uncertain returns
- Available at Avanza, Nordnet, banks

**KF (Kapitalförsäkring) - Capital Insurance:**
- Similar flat tax structure to ISK
- Additional insurance wrapper
- Beneficial for estate planning
- Can hold alternative investments

**AF (Aktie- och Fondkonto) - Regular Account:**
- Pay tax on actual profits (30% capital gains tax)
- Better if you plan to realize losses for tax purposes

**Where to Learn More:**
- Skatteverket.se - Official Swedish Tax Agency information
- Avanza.se/lar-dig-mer/avanza-akademin
- Nordnet.se/learn
                """
                result["recommendation"] = "ISK is generally recommended for most Swedish investors due to simplicity and tax advantages."
                return result

            # General fallback response
            result["information"] = f"""
**Finding Information About: "{query}"**

**Recommended Resources:**

**Swedish Financial Information:**
- Avanza.se - Investment platform with educational content
- Nordnet.se - Nordic investment platform
- Compricer.se - Compare financial products
- Konsumenternas.se - Swedish Consumer Agency
- Rikatillsammans.se - Swedish investment community

**International Financial Information:**
- Investopedia.com - Financial education
- Morningstar.com - Investment research
- Yahoo Finance - Market data and news

**Official Sources:**
- Skatteverket.se - Swedish Tax Agency
- Finansinspektionen.se - Swedish Financial Supervisory Authority
            """
            result["recommendation"] = "For the most current and accurate information, always verify with official sources and the specific financial institutions you're interested in."

            return result

        except Exception as e:
            return {"error": f"Error providing financial information: {str(e)}"}

    def _compare_institutions(self, inst1: str, inst2: str, comparison_type: str) -> Dict[str, Any]:
        """
        Compare two financial institutions or products.
        """
        try:
            result = {
                "institution1": inst1,
                "institution2": inst2,
                "comparison_type": comparison_type,
                "comparison": {
                    "note": "For the most accurate and up-to-date comparison, please check the official websites",
                    "factors_to_consider": []
                }
            }

            # Add relevant comparison factors based on type
            if "savings" in comparison_type.lower() or "sparande" in comparison_type.lower():
                result["comparison"]["factors_to_consider"] = [
                    "Interest rate (ränta)",
                    "Withdrawal limits",
                    "Minimum deposit requirements",
                    "Fees (avgifter)",
                    "Deposit insurance coverage",
                    "Digital accessibility (mobile app, web)"
                ]
            elif "isk" in comparison_type.lower():
                result["comparison"]["factors_to_consider"] = [
                    "Trading fees (courtage)",
                    "Available markets (Swedish, US, European stocks)",
                    "Number of available funds",
                    "Platform usability",
                    "Research tools and analysis",
                    "Customer service"
                ]
            elif "platform" in comparison_type.lower():
                result["comparison"]["factors_to_consider"] = [
                    "Account types offered (ISK, KF, regular account)",
                    "Trading fees structure",
                    "Available investment products",
                    "Educational resources",
                    "Mobile app quality",
                    "Customer support",
                    "Minimum deposit requirements"
                ]
            else:
                result["comparison"]["factors_to_consider"] = [
                    "Fees and costs",
                    "Service quality",
                    "Digital features",
                    "Customer reviews",
                    "Accessibility"
                ]

            result["recommendation"] = (
                f"To compare {inst1} and {inst2} for {comparison_type}, "
                f"I recommend checking these factors: {', '.join(result['comparison']['factors_to_consider'][:3])}. "
                f"Visit their official websites for the most current information."
            )

            return result

        except Exception as e:
            return {"error": f"Error comparing institutions: {str(e)}"}
