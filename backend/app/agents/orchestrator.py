from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent
from .sql_analyst import SQLAnalystAgent
from .financial_advisor import FinancialAdvisorAgent
from app.services.chat_data_service import ChatDataService
import json


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Routes user queries to appropriate specialized agents.
    Coordinates multi-agent responses and maintains conversation flow.
    """

    def __init__(self, data_service: ChatDataService):
        # Get user profile IMMEDIATELY to provide context
        user_profile = data_service.get_user_profile()

        # Get current date/time in user's timezone
        from datetime import datetime
        import pytz

        user_timezone = user_profile.get('timezone', 'UTC')
        try:
            tz = pytz.timezone(user_timezone)
            now = datetime.now(tz)
        except:
            # Fallback to UTC if timezone is invalid
            now = datetime.now(pytz.UTC)
            user_timezone = 'UTC'

        current_date = now.strftime("%Y-%m-%d")
        current_month = now.strftime("%Y-%m")
        current_month_name = now.strftime("%B %Y")
        current_time = now.strftime("%H:%M:%S")

        user_context = f"""
CURRENT DATE & TIME (CRITICAL - YOU MUST KNOW THIS):
- Today's Date: {current_date}
- Current Time: {current_time}
- Current Month: {current_month_name} ({current_month})
- Day of Week: {now.strftime("%A")}
- Timezone: {user_timezone}

IMPORTANT USER CONTEXT (MEMORIZE THIS):
- User Name: {user_profile.get('full_name', 'User')}
- Currency: {user_profile.get('currency', 'SEK')}
- Timezone: {user_timezone}
- Household Members: {user_profile.get('household_info', {}).get('household_members', 'Not specified')}
- Vehicles: {user_profile.get('household_info', {}).get('num_vehicles', 'Not specified')}
- Housing Type: {user_profile.get('household_info', {}).get('housing_type', 'Not specified')}
- House Size: {user_profile.get('household_info', {}).get('house_size_sqm', 'Not specified')} sqm
- Monthly Income Goal: {user_profile.get('financial_goals', {}).get('monthly_income_goal', 'Not set')}
- Monthly Savings Goal: {user_profile.get('financial_goals', {}).get('monthly_savings_goal', 'Not set')}

CRITICAL: Always use {user_profile.get('currency', 'SEK')} when displaying amounts!
CRITICAL: All date/time references are in user's timezone ({user_timezone})!
        """

        super().__init__(
            name="Financial Assistant Orchestrator",
            role="Intelligent Query Router and Coordinator",
            instructions=f"""{user_context}

You are the main orchestrator for a multi-agent financial assistant system.

Your role:
- Understand user queries and determine which specialized agent(s) to invoke
- Route data analysis questions to the SQL Analyst
- Route financial advice questions to the Financial Advisor
- Combine insights from multiple agents when needed
- Provide direct answers for simple greetings or general questions

Available Agents:
1. SQL Analyst: Expert at analyzing spending patterns, data breakdowns, and database queries
   - Use for: "How much did I spend?", "Show my category breakdown", "What are my trends?"

2. Financial Advisor: Expert at providing financial advice and recommendations
   - Use for: "How can I save more?", "Is my budget healthy?", "Financial advice"

Decision Rules:
- If the user asks for DATA or ANALYSIS → route to SQL Analyst
- If the user asks for ADVICE or RECOMMENDATIONS → route to Financial Advisor
- If the query needs BOTH data analysis AND advice → use both agents
- For greetings or simple questions → respond directly without invoking agents

When invoking agents:
1. Choose the appropriate agent(s) based on query intent
2. Formulate a clear question for each agent
3. Wait for agent responses
4. Synthesize responses into a coherent answer for the user
5. Maintain a friendly, helpful tone
6. ALWAYS reference user's name and use their currency"""
        )
        self.data_service = data_service
        self.sql_analyst = SQLAnalystAgent(data_service)
        self.financial_advisor = FinancialAdvisorAgent(data_service)

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define agent invocation functions"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "consult_sql_analyst",
                    "description": "Consult the SQL Analyst for data analysis, spending patterns, breakdowns, and trends",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The specific question to ask the SQL Analyst"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consult_financial_advisor",
                    "description": "Consult the Financial Advisor for budget advice, savings optimization, and financial recommendations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The specific question to ask the Financial Advisor"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute agent consultation"""
        query = arguments.get("query", "")

        if function_name == "consult_sql_analyst":
            response = self.sql_analyst.chat(query)
            return {"agent": "SQL Analyst", "response": response}

        elif function_name == "consult_financial_advisor":
            response = self.financial_advisor.chat(query)
            return {"agent": "Financial Advisor", "response": response}

        else:
            return {"error": f"Unknown function: {function_name}"}

    def chat(self, user_message: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Enhanced chat method that returns structured response with agent info.
        """
        self.add_message("user", user_message)

        messages = [self.get_system_message()] + self.conversation_history
        agents_consulted = []
        agent_timeline = []  # Track the order and timing of agent consultations

        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.get_tools(),
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # Check if the model wants to call functions
            if assistant_message.tool_calls:
                # Add assistant's message to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ]
                })

                # Execute each function call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute the function
                    function_response = self.execute_function(function_name, arguments)

                    # Track which agents were consulted
                    if isinstance(function_response, dict) and "agent" in function_response:
                        agent_name = function_response["agent"]
                        agents_consulted.append(agent_name)
                        agent_timeline.append({
                            "agent": agent_name,
                            "iteration": iteration + 1,
                            "status": "completed"
                        })

                    # Add function response to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_response)
                    })

            else:
                # No more function calls, return the final response
                final_response = assistant_message.content
                self.add_message("assistant", final_response)

                return {
                    "response": final_response,
                    "agents_consulted": list(set(agents_consulted)),
                    "agent_timeline": agent_timeline,
                    "iterations": iteration + 1
                }

        # If we've exhausted iterations
        return {
            "response": "I've processed your request but needed more iterations to complete. Please try rephrasing your question.",
            "agents_consulted": list(set(agents_consulted)),
            "agent_timeline": agent_timeline,
            "iterations": max_iterations
        }
