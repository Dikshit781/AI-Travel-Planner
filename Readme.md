# ✈️ AI Travel Planner

A chat-based travel planner that runs its language model **locally** with [Ollama](https://ollama.com). Tell it your destination, number of days, budget, interests and travel dates, and it creates a full trip plan. It also fetches live weather, converts currencies and answers follow-up questions about your plan.

It comes with two interfaces that share the same backend:

- **Web UI** built with Streamlit (`app.py`)
- **Terminal version** (`Travel_planner.py`)

---

## Features

- **Full trip plan** with a day-wise itinerary, budget breakdown, packing suggestions and local travel tips
- **Live weather** for your destination, via WeatherAPI
- **Currency conversion** (for example, INR to USD), via a free exchange-rate API
- **Conversation memory**: say "make it 7 days" or "change the budget to 60000" and only that detail updates
- **Follow-up questions** answered from your existing plan without regenerating it
- **Missing-detail check**: the app asks for anything you haven't provided yet
- **Quick actions** in the sidebar: convert budget, current weather, food suggestions
- **Download** your plan as a Markdown file
- **Private and free to run**: the model runs on your own machine

---

## Tech stack

| Component | Purpose |
|---|---|
| Python 3.10+ | Language |
| Ollama + `llama3.2` | Local LLM |
| LangChain (`langchain-ollama`, `langchain-core`) | Prompts, chains and tool calling |
| Streamlit | Web interface |
| WeatherAPI | Current weather data |
| open.er-api.com | Exchange rates |
| python-dotenv | Loads the API key from `.env` |
| requests | HTTP calls |

---

## Project structure

```
.
├── app.py               # Streamlit web interface
├── Travel_planner.py    # Backend: LLM, tools, prompts, logic, terminal app
├── .env                 # Your API key (you create this)
├── requirements.txt     # Python dependencies (optional, see below)
└── README.md
```

---

## Setup

### 1. Install Ollama and pull the model

Download Ollama from [ollama.com](https://ollama.com), then run:

```bash
ollama pull llama3.2
```

Make sure Ollama is running in the background before you start the app.

### 2. Get a free WeatherAPI key

Sign up at [weatherapi.com](https://www.weatherapi.com) and copy your API key.

### 3. Install the Python dependencies

Create a `requirements.txt` file with:

```
streamlit
langchain-ollama
langchain-core
python-dotenv
requests
```

Then install them (a virtual environment is recommended):

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Add your API key

Create a file named `.env` in the project folder:

```
WEATHER_API_KEY=your_weatherapi_key_here
```

---

## Running the app

### Web UI (recommended)

```bash
streamlit run app.py
```

It opens in your browser, usually at `http://localhost:8501`.

### Terminal version

```bash
python Travel_planner.py
```

Type `exit` to quit.

---

## How to use it

### 1. Create a plan

Include all five details: **destination, days, budget, interests and dates**.

```
Plan a 5 day trip to Goa with a budget of 40000 INR. I like beaches, seafood and nightlife. Travelling from 10 December to 15 December.
```

### 2. Ask follow-up questions

These are answered from your existing plan:

```
Convert my budget to USD
What is the weather like at my destination right now?
Suggest some good local food places for my trip
Which day is best for the beach?
```

### 3. Change the trip

Any change to a detail regenerates the plan:

```
Make it 7 days instead
Change my budget to 60000 INR
Add trekking to my interests
```

### 4. Missing details

```
Plan a trip to Goa
```

The app replies: `Please provide: days, budget, interests, dates`

---

## How it works

```
User message
     │
     ▼
details_chain ──► extracts trip details as JSON ──► updates memory
     │
     ├── details missing?  ──► asks the user for them
     │
     ├── new or changed details? ──► get weather (tool) ──► plan_chain writes the plan
     │
     └── nothing changed (a question)? ──► answer_query uses the plan + tools
```

Key pieces in `Travel_planner.py`:

| Piece | Role |
|---|---|
| `llm` | The single Ollama model used for extraction, planning and answers |
| `get_weather` / `currency_convert` | Tools the model can request |
| `tool_map` | Lets the code find a tool by the name the model asks for |
| `tool_llm` | The model bound to the tools |
| `details_chain` | Turns free text into structured trip details |
| `plan_chain` | Writes the travel plan |
| `run_with_tools()` | Loop that runs requested tools and feeds the results back to the model |
| `parse_json()` | Pulls the JSON block out of the model's reply |
| `process_message()` | Main entry point shared by the terminal and Streamlit apps |

`app.py` uses Streamlit's `session_state` to keep the chat history, trip details and plan between page re-runs.

---

## Configuration

| Setting | Where | Default |
|---|---|---|
| Model name | `MODEL_NAME` in `Travel_planner.py` | `llama3.2` |
| Temperature | `ChatOllama(...)` in `Travel_planner.py` | `0.2` |
| Default currency | `new_memory()` in `Travel_planner.py` | `INR` |
| API key | `.env` | none (required for weather) |

To use a different model, run `ollama pull <model>` and change `MODEL_NAME`. The model must support **tool calling**.

---

## Troubleshooting

**"Sorry, something went wrong. Make sure Ollama is running..."**
Start Ollama and confirm the model is pulled with `ollama list`.

**"WEATHER_API_KEY not found in your .env file"**
Check that `.env` is in the same folder you run the app from and that the variable name is exactly `WEATHER_API_KEY`.

**`Weather error: 401` or `403`**
Your API key is invalid or not activated yet.

**`No JSON found` or a JSON decode error**
A small local model sometimes returns malformed output. Resend your message. If it happens often, try a larger model, or force JSON mode for extraction:

```python
details_chain = details_prompt | llm.bind(format="json")
```

**The budget breakdown doesn't add up**
Small models can be weak at arithmetic. Try a larger model, or ask the app to fix the breakdown.

**`ModuleNotFoundError`**
Activate your virtual environment and run `pip install -r requirements.txt` again.

---

## Known limitations

- A small local model (3B parameters) can be inconsistent with JSON extraction, tool calling and arithmetic.
- The tool loop has no round limit, and an invented tool name would raise a `KeyError`.
- Weather is current conditions only, not a forecast for your travel dates.
- Exchange rates are approximate market rates.

---

## Possible improvements

- Add a weather forecast for the travel dates
- Add more tools (hotels, flights, maps)
- Validate the JSON output with Pydantic
- Add a maximum number of tool rounds and handle unknown tool names
- Export the plan as PDF

---

## License

Add your preferred license here (for example, MIT).