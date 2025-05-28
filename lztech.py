
import streamlit as st
import datetime
import json
import os

# Caminho do arquivo de dados
DATA_FILE = "dados.json"

# Carregar os dados existentes (ou iniciar vazio)
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"valores": []}

# Função para salvar os dados
def salvar_dados():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Interface do aplicativo
st.set_page_config(page_title="LZTech Chatbot", layout="centered")

# Mensagem de boas-vindas
st.markdown(f"""
# 🤖 Bem-vindo ao LZTech
📅 Data: {datetime.datetime.now().strftime("%d/%m/%Y")}
""")

# Opções de ações disponíveis
st.markdown("### Ações disponíveis:")
st.markdown("""
- ➕ **Adicionar valor**
- 📊 **Ver todos os dados**
- ➗ **Ver a soma total**
""")

# Escolha de ação
acao = st.selectbox("Escolha uma ação:", ["Adicionar valor", "Ver todos os dados", "Ver a soma total"])

# Lógica das ações
if acao == "Adicionar valor":
    valor = st.number_input("Digite um valor numérico para adicionar:", step=1.0)
    if st.button("Adicionar"):
        data["valores"].append(valor)
        salvar_dados()
        st.success(f"Valor {valor} adicionado com sucesso!")

elif acao == "Ver todos os dados":
    st.write("### 📋 Valores armazenados:")
    if data["valores"]:
        st.write(data["valores"])
    else:
        st.info("Nenhum valor armazenado ainda.")

elif acao == "Ver a soma total":
    total = sum(data["valores"])
    st.metric("🔢 Soma total dos dados:", total)
