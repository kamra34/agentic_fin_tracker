from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings


class BaseAgent(ABC):
    """Base class for all AI agents"""

    def __init__(self, name: str, role: str, instructions: str):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.MODEL_ID
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_system_message(self) -> Dict[str, str]:
        """Get the system message for this agent"""
        return {
            "role": "system",
            "content": f"You are {self.name}, a {self.role}.\n\n{self.instructions}"
        }

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Define the tools/functions this agent can use"""
        pass

    @abstractmethod
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a function call"""
        pass

    def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Main chat method with function calling support.
        Handles multiple iterations of function calls.
        """
        self.add_message("user", user_message)

        messages = [self.get_system_message()] + self.conversation_history

        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.get_tools() if self.get_tools() else None,
                tool_choice="auto" if self.get_tools() else None,
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
                    import json
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute the function
                    function_response = self.execute_function(function_name, arguments)

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
                return final_response

        # If we've exhausted iterations, return what we have
        return "I've processed your request but needed more iterations to complete. Please try rephrasing your question."
