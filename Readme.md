# AI Travel Planner ✈️

An AI-powered travel planning assistant that generates personalized travel itineraries based on user preferences, budget, destination, and trip duration.

## Features

- Personalized travel itinerary generation
- Weather information using tool calling
- Conversational travel assistant
- Memory management to remember travel preferences
- Dynamic itinerary regeneration when travel details change
- Currency conversion through tools
- Follow-up question answering using existing travel plans

## Tech Stack

- Python
- LangChain
- Large Language Models (LLMs)
- Ollama
- Tool Calling
- JSON
- Weather API / Tool
- Currency Conversion Tool

## Project Workflow

1. Collect travel details from the user.
2. Extract and update information using an LLM.
3. Store user preferences in memory.
4. Fetch destination weather information.
5. Generate a personalized travel itinerary.
6. Answer follow-up questions using the existing plan and available tools.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/AI-Travel-Planner.git
cd AI-Travel-Planner
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your required API keys and environment variables in a `.env` file.

Run the application:

```bash
python main.py
```

## Future Improvements

- Streamlit-based user interface
- Hotel and flight recommendations
- Location-based recommendations
- Trip expense tracking

## Author

Dikshit Dhiman