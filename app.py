import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values

env = dotenv_values(".env")

openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

st.title(":black_joker: NaszGPT z OpenAI")

def get_chatbot_reply(user_prompt: str):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
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
    with st.chat_message("human"):
        st.markdown(prompt)

    st.session_state["messages"].append({
        "role": "human",
        "content": prompt
    })

    # wyświetlenie odpowiedzi AI
    with st.chat_message("assistant"):
        chatbot_message = get_chatbot_reply(prompt)
        st.markdown(chatbot_message["content"])

    st.session_state["messages"].append(chatbot_message)
    