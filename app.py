import streamlit as st


st.title(":parrot: Papuga!")

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
    with st.chat_message("ai"):
        response = f"Papuga mówi {prompt}"
        st.markdown(response)

    st.session_state["messages"].append({"role": "ai", "content": response})
    