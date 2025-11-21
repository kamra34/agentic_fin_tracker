from typing import List, Dict, Any
from .base_agent import BaseAgent
from app.services.chat_data_service import ChatDataService


class SQLAnalystAgent(BaseAgent):
    """
    SQL Analyst Agent - Analyzes database structure and provides data insights.
    Can only READ data, no write operations allowed.
    """

    def __init__(self, data_service: ChatDataService):
        # Get user context immediately
        user_profile = data_service.get_user_profile()
        user_context = f"""
CRITICAL USER CONTEXT - ALWAYS USE THIS:
- User's Name: {user_profile.get('full_name', 'User')}
- User's Currency: {user_profile.get('currency', 'SEK')} (MUST use this for ALL amounts)
- Household Size: {user_profile.get('household_info', {}).get('household_members', 'Not specified')}
- Number of Vehicles: {user_profile.get('household_info', {}).get('num_vehicles', 'Not specified')}
- Housing: {user_profile.get('household_info', {}).get('housing_type', 'Not specified')}
- House Size: {user_profile.get('household_info', {}).get('house_size_sqm', 'Not specified')} sqm

REMEMBER: The user's currency is {user_profile.get('currency', 'SEK')}. Display ALL amounts in {user_profile.get('currency', 'SEK')}.
        """

        super().__init__(
            name="SQL Analyst",
            role="Database and Data Analysis Expert",
            instructions=f"""{user_context}

You are an expert SQL analyst for {user_profile.get('full_name', 'the user')}'s personal financial tracking system.

Your responsibilities:
- Analyze spending patterns and trends
- Provide detailed breakdowns by categories, accounts, and time periods
- Answer questions about the database structure
- Suggest data-driven insights based on the user's financial data
- Consider household context (family size, vehicles, housing) when providing insights

IMPORTANT CONSTRAINTS:
- You can ONLY READ data from the database
- You CANNOT perform any CREATE, UPDATE, DELETE operations
- You CANNOT modify user data in any way
- You can only analyze and report on existing data

Available database tables:
- users: User profiles with financial goals
- expenses: Daily expense records with categories and amounts
- categories/subcategories: Expense categorization
- accounts: Payment accounts (bank, credit cards)
- savings_accounts: Investment and savings accounts
- savings_transactions: Deposits, withdrawals, value updates
- income_templates: Recurring income sources
- monthly_incomes: Actual monthly income entries
- expense_templates: Recurring expense templates

When answering questions:
1. ALWAYS call get_user_profile() FIRST to get complete user context
2. For "current income" or "monthly income" questions → use get_current_income_sources()
3. For historical income analysis → use get_income_summary(month="YYYY-MM")
4. Use the available functions to retrieve relevant data
5. Analyze the data and identify patterns or insights
6. Present findings in a clear, concise manner
7. ALWAYS use {user_profile.get('currency', 'SEK')} when displaying amounts (NEVER convert currencies!)
8. Reference the user by name when appropriate
9. Consider household context in your analysis

CRITICAL: All amounts in the database are ALREADY in the user's currency ({user_profile.get('currency', 'SEK')}). NEVER convert or assume USD!"""
        )
        self.data_service = data_service

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define available data retrieval functions"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_database_schema",
                    "description": "Get complete database schema information including all tables and columns",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_profile",
                    "description": "Get user's profile including financial goals and household information",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_spending_summary",
                    "description": "Get spending summary for a date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (optional)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format (optional)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_category_breakdown",
                    "description": "Get spending breakdown by category for a date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (optional)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format (optional)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_subcategory_breakdown",
                    "description": "Get spending breakdown by subcategory, optionally filtered by category",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category_name": {
                                "type": "string",
                                "description": "Filter by specific category name (optional)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_account_summary",
                    "description": "Get spending summary by payment account",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_monthly_trends",
                    "description": "Get monthly spending trends for the last N months",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "months": {
                                "type": "integer",
                                "description": "Number of months to retrieve (default: 6)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_savings_summary",
                    "description": "Get complete savings and investment summary with profit/loss",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_income_sources",
                    "description": "Get CURRENT recurring monthly income sources and amounts (NOT historical totals). Use this when user asks about 'current income' or 'monthly income'.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_income_summary",
                    "description": "Get income summary for a SPECIFIC month (YYYY-MM format). Use this for historical income analysis, NOT for current income.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "month": {
                                "type": "string",
                                "description": "Month in YYYY-MM format (optional, defaults to current month)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_expense_templates",
                    "description": "Get all recurring expense templates",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a data retrieval function"""
        if function_name == "get_database_schema":
            return self.data_service.get_database_schema()
        elif function_name == "get_user_profile":
            return self.data_service.get_user_profile()
        elif function_name == "get_current_income_sources":
            return self.data_service.get_current_income_sources()
        elif function_name == "get_spending_summary":
            return self.data_service.get_spending_summary(
                arguments.get("start_date"),
                arguments.get("end_date")
            )
        elif function_name == "get_category_breakdown":
            return self.data_service.get_category_breakdown(
                arguments.get("start_date"),
                arguments.get("end_date")
            )
        elif function_name == "get_subcategory_breakdown":
            return self.data_service.get_subcategory_breakdown(
                arguments.get("category_name")
            )
        elif function_name == "get_account_summary":
            return self.data_service.get_account_summary()
        elif function_name == "get_monthly_trends":
            return self.data_service.get_monthly_trends(
                arguments.get("months", 6)
            )
        elif function_name == "get_savings_summary":
            return self.data_service.get_savings_summary()
        elif function_name == "get_income_summary":
            return self.data_service.get_income_summary(
                arguments.get("month")
            )
        elif function_name == "get_expense_templates":
            return self.data_service.get_expense_templates()
        else:
            return {"error": f"Unknown function: {function_name}"}
