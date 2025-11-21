from typing import List, Dict, Any
from .base_agent import BaseAgent
from app.services.chat_data_service import ChatDataService


class FinancialAdvisorAgent(BaseAgent):
    """
    Financial Advisor Agent - Provides financial advice and recommendations.
    Focuses on budget analysis, savings optimization, and financial health.
    """

    def __init__(self, data_service: ChatDataService):
        super().__init__(
            name="Financial Advisor",
            role="Personal Finance Advisor",
            instructions="""You are an expert personal financial advisor specializing in budgeting, savings, and financial wellness.

Your responsibilities:
- Analyze user's financial health and provide actionable advice
- Suggest budget optimizations and spending improvements
- Help users achieve their savings goals
- Provide insights on income vs expenses
- Recommend strategies for better financial management

IMPORTANT CONSTRAINTS:
- You can ONLY READ data from the database
- You CANNOT perform any CREATE, UPDATE, DELETE operations
- You CANNOT modify user data in any way
- You can only provide advice based on existing data

Your approach:
1. Gather relevant financial data using available functions
2. Analyze spending patterns, savings, and income
3. Calculate financial health metrics
4. Provide personalized, actionable recommendations
5. Use encouraging and supportive language
6. Consider the user's goals and household situation

When providing advice:
- Be specific and actionable
- Prioritize the most impactful recommendations
- Consider the user's currency and local context
- Acknowledge progress and celebrate wins
- Be realistic about achievable goals
- Explain the "why" behind recommendations"""
        )
        self.data_service = data_service

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define available functions for financial analysis"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_user_profile",
                    "description": "Get user's profile including financial goals, household info, and currency",
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
                    "name": "get_financial_health_metrics",
                    "description": "Get comprehensive financial health metrics including income, expenses, savings rate, and goals",
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
                    "name": "get_category_breakdown",
                    "description": "Get spending breakdown by category to identify optimization opportunities",
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
                    "name": "get_monthly_trends",
                    "description": "Get monthly spending trends to identify patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "months": {
                                "type": "integer",
                                "description": "Number of months to analyze (default: 6)"
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
                    "description": "Get savings and investment summary with profit/loss analysis",
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
                    "description": "Get income summary for budget analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "month": {
                                "type": "string",
                                "description": "Month in YYYY-MM format (optional)"
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
                    "description": "Get recurring expense templates to analyze fixed costs",
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
                    "description": "Get overall spending summary for a period",
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
            }
        ]

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a financial analysis function"""
        if function_name == "get_user_profile":
            return self.data_service.get_user_profile()
        elif function_name == "get_financial_health_metrics":
            return self.data_service.get_financial_health_metrics()
        elif function_name == "get_category_breakdown":
            return self.data_service.get_category_breakdown(
                arguments.get("start_date"),
                arguments.get("end_date")
            )
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
        elif function_name == "get_spending_summary":
            return self.data_service.get_spending_summary(
                arguments.get("start_date"),
                arguments.get("end_date")
            )
        else:
            return {"error": f"Unknown function: {function_name}"}
