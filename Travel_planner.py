import os
import re
import json
import requests

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool

load_dotenv()

WEATHER_KEY = os.getenv("WEATHER_API_KEY")
MODEL_NAME = os.getenv("MODEL")

llm = ChatOllama(model=MODEL_NAME, temperature=0.4)
json_llm = ChatOllama(model=MODEL_NAME, temperature=0, format="json")


# --------------------------------------------------
# Tools
# --------------------------------------------------

@tool
def get_weather(city: str) -> str:
    """Get current temperature and weather condition of a city."""

    url = "https://api.weatherapi.com/v1/current.json"

    try:
        response = requests.get(
            url,
            params={"key": WEATHER_KEY, "q": city},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        return (
            f"Temperature: {data['current']['temp_c']}°C\n"
            f"Condition: {data['current']['condition']['text']}"
        )

    except Exception as error:
        return f"Weather error: {error}"


@tool
def currency_convert(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert currency from one type to another.
    """

    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"

        response = requests.get(url, timeout=10)
        data = response.json()

        rate = data["rates"][to_currency.upper()]

        converted = amount * rate

        return (
            f"{amount} {from_currency.upper()} = "
            f"{converted:.2f} {to_currency.upper()}"
        )

    except Exception as e:
        return f"Conversion failed: {str(e)}"


tools = [get_weather, currency_convert]
tool_map = {t.name: t for t in tools}

tool_llm = llm.bind_tools(tools)


# --------------------------------------------------
# Prompts and chains
# --------------------------------------------------

details_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Extract trip details as JSON with exactly these keys:
destination, days, budget, currency, interests, dates.
Use old details when the user does not change them.
If the user is only asking a question, return the old details unchanged.
Return JSON only."""
    ),
    (
        "human",
        "Old details: {old_details}\nUser: {input}"
    )
])

plan_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Create a travel plan with:
1. Day-wise itinerary
2. Budget breakdown
3. Packing suggestions
4. Local travel tips
The budget breakdown amounts MUST add up to exactly the given budget.
Never exceed the budget. Use only the given currency."""
    ),
    (
        "human",
        """Destination: {destination}
Days: {days}
Budget: {budget} {currency}
Interests: {interests}
Dates: {dates}
Weather: {weather}"""
    )
])

details_chain = details_prompt | json_llm
plan_chain = plan_prompt | llm


# --------------------------------------------------
# Core logic (used by both the terminal app and the Streamlit UI)
# --------------------------------------------------

REQUIRED_FIELDS = ["destination", "days", "budget", "interests", "dates"]


def new_memory():
    return {
        "destination": "",
        "days": "",
        "budget": "",
        "currency": "INR",
        "interests": "",
        "dates": ""
    }


def parse_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group(0))


def run_with_tools(messages):
    response = tool_llm.invoke(messages)

    while response.tool_calls:
        messages.append(response)

        for call in response.tool_calls:
            result = tool_map[call["name"]].invoke(call["args"])

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call["id"]
                )
            )

        response = tool_llm.invoke(messages)

    return response.content


def call_tools(message):
    return run_with_tools([HumanMessage(content=message)])


def generate_plan(memory):
    """Returns the weather line followed by the full travel plan as text."""
    weather = call_tools(
        f"Use the weather tool for {memory['destination']}. "
        "Display only temperature and condition."
    )
    plan = plan_chain.invoke({**memory, "weather": weather})
    return f"Current weather: {weather}\n\n---\n\n{plan.content}"


def answer_query(question, memory, plan):
    messages = [
        SystemMessage(content=(
            "You are a helpful travel assistant. Answer the user's question "
            "using the trip details and plan below. Use tools for weather "
            "or currency conversion when needed.\n\n"
            f"Trip details: {json.dumps(memory)}\n\n"
            f"Current plan:\n{plan}"
        )),
        HumanMessage(content=question)
    ]
    return run_with_tools(messages)


def process_message(user_input, memory, current_plan):
    """
    Handle one user message.

    Updates `memory` in place and returns (reply, plan):
      - reply: text to show the user
      - plan:  the current plan (new if regenerated, otherwise unchanged)
    Raises an exception if details cannot be extracted (e.g. Ollama is down).
    """
    old_memory = dict(memory)

    response = details_chain.invoke({
        "old_details": json.dumps(memory),
        "input": user_input
    })
    new_details = parse_json(response.content)

    for key, value in new_details.items():
        if key in memory and value:
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            memory[key] = value

    # Only accept a currency change if the budget changed in the same
    # message. Otherwise it is a conversion request.
    if memory["budget"] == old_memory["budget"]:
        memory["currency"] = old_memory["currency"]

    missing = [key for key in REQUIRED_FIELDS if not memory[key]]
    if missing:
        return "Please provide: " + ", ".join(missing), current_plan

    if current_plan is None or memory != old_memory:
        plan = generate_plan(memory)
        return plan, plan

    return answer_query(user_input, memory, current_plan), current_plan


# --------------------------------------------------
# Terminal version
# --------------------------------------------------

def main():
    memory = new_memory()
    current_plan = None

    print("AI Travel Planner")
    print("Enter trip details or type 'exit'.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "exit":
            print("AI: Have a Nice Trip 😊!!!")
            break

        try:
            reply, current_plan = process_message(
                user_input, memory, current_plan
            )
        except Exception as error:
            print("DEBUG error:", error)
            print("AI: Please provide valid trip details.")
            continue

        print("\nAI:", reply)


if __name__ == "__main__":
    main()