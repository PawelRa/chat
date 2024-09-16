import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values
import json
from pathlib import Path


model_pricings = {
    "gpt-4o":{
        "input_tokens": 5.00 / 1_000_000, #per token
        "output_tokens": 15.00 / 1_000_000, #per token
    },
    "gpt-4o-mini":{
        "input_tokens": 0.150 / 1_000_000, #per token
        "output_tokens": 0.600 / 1_000_000, # per token
    }
}
MODEL = "gpt-4o-mini"
USD_TO_PLN = 3.97
PRICING = model_pricings[MODEL]

env = dotenv_values(".env")

openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

st.title(":floppy_disk: NaszGPT pamięta rozmowę")

def get_chatbot_reply(user_prompt, memory):
    # dodaj system messages
    messages=[
        {
            "role": "system",
            "content": st.session_state["chatbot_personality"],
        },
    ]
    # Dodawanie wszystkich wiadomości z pamięci
    for message in memory:
        messages.append({"role": message["role"], 
                         "content": message["content"]
                         })
        
    # dodawanie wiadomości użytkownika
    messages.append({"role": "user", "content": user_prompt})

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=messages
    )  
    usage = {}
    if response.usage:
        usage = {
            # INPUT
            "prompt_tokens": response.usage.prompt_tokens,
            # OUTPUT
            "completion_tokens": response.usage.completion_tokens,
            # INPUT + OUTPUT
            "total_tokens": response.usage.total_tokens,
        }

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
        "usage": usage,
    }

if "messages" not in st.session_state:
    if Path("current_conversation.json").exists():
        with open("current_conversation.json", "r") as f:
            chatbot_conversation = json.loads(f.read())

        st.session_state["messages"] = chatbot_conversation["messages"]
        st.session_state["chatbot_personality"] = chatbot_conversation["chatbot_personality"]

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("O co chcesz zapytać?")
if prompt:
    # wyświetlanie wiadomości od użytkownika
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append({
        "role": "user",
        "content": prompt
    })

    # wyświetlenie odpowiedzi AI
    with st.chat_message("assistant"):
        chatbot_message = get_chatbot_reply(
            prompt,
            memory=st.session_state["messages"][-10:]
            )
        st.markdown(chatbot_message["content"])

    st.session_state["messages"].append({
        "role": "assistant", 
        "content": chatbot_message["content"], 
        "usage": chatbot_message["usage"]
        })
    
    with open("current_conversation.json", "w") as f:
        f.write(json.dumps({
            "chatbot_personality": st.session_state["chatbot_personality"],
            "messages": st.session_state["messages"],
        }))

with st.sidebar:
    st.write("Aktualny model", MODEL)
    total_cost = 0
    for message in st.session_state["messages"]:
        if "usage" in message:
            total_cost += message["usage"]["prompt_tokens"] * PRICING["input_tokens"]
            total_cost += message["usage"]["completion_tokens"] * PRICING["output_tokens"]

    c0, c1 = st.columns(2)
    with c0:
        st.metric("Koszt rozmowy (USD)", f"${total_cost:.4f}")

    with c1:
        st.metric("Koszt rozmowy (PLN)", f"{total_cost * USD_TO_PLN:.4f}")

    st.session_state["chatbot_personality"] = st.text_area(
        "Opisz osobowość chatbota",
        max_chars=1000,
        height=200,
        value="""
        Jesteś pomocnikiem, który odpowiada na wszystkie pytania użytkownika. Odpowiadaj na pytania w sposób zwięzły i zrozumiały.
        """.strip()
    )
