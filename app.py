import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values

env = dotenv_values(".env")

openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

st.title(":brain: NaszGPT z pamięcią")

def get_chatbot_reply(user_prompt, memory):
    # system messages
    messages=[
        {
            "role": "system",
            "content": """"
            Jesteś pomocnikiem, który odpowiada na wszystkie pytania użytkownika.
                Odpowiadaj na pytania w sposób zwięzły i zrozumiały.
            """
        },
        {"role": "user", "content": user_prompt}
    ]
    # Dodawanie wszystkich wiadomości z pamięci
    for message in memory:
        messages.append({"role": message["role"], 
                         "content": message["content"]
                         })
        
    # dodawanie wiadomości użytkownika
    messages.append({"role": "user", "content": user_prompt})

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )  

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
    }


if "messages" not in st.session_state:
    st.session_state["messages"] = []

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

    st.session_state["messages"].append(chatbot_message)
    

with st.sidebar:
    with st.expander("Historia rozmowy"):
        st.json(st.session_state.get("messages" or []))
