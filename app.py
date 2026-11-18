import streamlit as st

from Travel_planner import (
    MODEL_NAME,
    WEATHER_KEY,
    new_memory,
    process_message,
)

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")

WELCOME = (
    "Hi! I'm your AI travel planner. Tell me your **destination, number of days, "
    "budget, interests and travel dates** and I'll plan your trip.\n\n"
    "Example: *Plan a 5 day trip to Goa with a budget of 40000 INR. "
    "I like beaches, seafood and nightlife. Travelling from 10 December to 15 December.*"
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

def reset_state():
    st.session_state.memory = new_memory()
    st.session_state.plan = None
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
    st.session_state.pending = None


if "memory" not in st.session_state:
    reset_state()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.title("✈️ Trip Details")

    mem = st.session_state.memory
    labels = {
        "destination": "📍 Destination",
        "days": "🗓️ Days",
        "budget": "💰 Budget",
        "interests": "🎯 Interests",
        "dates": "📅 Dates",
    }
    for key, label in labels.items():
        value = mem[key] or "—"
        if key == "budget" and mem[key]:
            value = f"{mem['budget']} {mem['currency']}"
        st.markdown(f"**{label}**  \n{value}")

    if not WEATHER_KEY:
        st.warning("WEATHER_API_KEY not found in your .env file.")

    st.divider()
    st.caption("Quick actions")

    if st.session_state.plan:
        if st.button("💱 Convert budget to USD", use_container_width=True):
            st.session_state.pending = "Convert my budget to USD"
            st.rerun()
        if st.button("🌦️ Current weather", use_container_width=True):
            st.session_state.pending = "What is the weather like at my destination right now?"
            st.rerun()
        if st.button("🍤 Food suggestions", use_container_width=True):
            st.session_state.pending = "Suggest some good local food places for my trip"
            st.rerun()

        st.download_button(
            "⬇️ Download plan",
            data=st.session_state.plan,
            file_name="travel_plan.md",
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        st.caption("Quick actions appear after your first plan.")

    st.divider()
    if st.button("🔄 Start new trip", use_container_width=True):
        reset_state()
        st.rerun()


# --------------------------------------------------
# Chat area
# --------------------------------------------------

st.title("AI Travel Planner")
st.caption(f"Powered by {MODEL_NAME} running locally with Ollama")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

pending = st.session_state.pending
st.session_state.pending = None
prompt = st.chat_input("Describe your trip or ask a question...") or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply, st.session_state.plan = process_message(
                    prompt,
                    st.session_state.memory,
                    st.session_state.plan,
                )
            except Exception as error:
                reply = (
                    "Sorry, something went wrong. Make sure Ollama is running "
                    f"and `{MODEL_NAME}` is pulled.\n\n`{error}`"
                )
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()  # refresh the sidebar with the updated trip details