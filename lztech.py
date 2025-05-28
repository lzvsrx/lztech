
import streamlit as st
import datetime
import json
import os
import pandas as pd
import hashlib
import matplotlib.pyplot as plt

# Função para criptografar senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Caminho base dos dados
DATA_DIR = "dados_usuarios"
os.makedirs(DATA_DIR, exist_ok=True)

# Mensagem de boas-vindas
st.set_page_config(page_title="LZTech Chatbot", layout="centered")
st.markdown(f"# 🤖 Bem-vindo ao LZTech\n📅 Data: {datetime.datetime.now().strftime('%d/%m/%Y')}")

# Autenticação
st.sidebar.header("🔐 Login ou Cadastro")
username = st.sidebar.text_input("Usuário")
password = st.sidebar.text_input("Senha", type="password")
action = st.sidebar.radio("Ação", ["Login", "Cadastrar"])

user_file = os.path.join(DATA_DIR, f"{username}.json")

# Função para carregar dados
def carregar_dados():
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            return json.load(f)
    else:
        return {"senha": "", "valores": []}

# Função para salvar dados
def salvar_dados(dados):
    with open(user_file, "w") as f:
        json.dump(dados, f)

# Login ou cadastro
if username and password:
    dados = carregar_dados()
    senha_hash = hash_password(password)

    if action == "Cadastrar":
        if os.path.exists(user_file):
            st.sidebar.warning("Usuário já existe.")
        else:
            salvar_dados({"senha": senha_hash, "valores": []})
            st.sidebar.success("Cadastro realizado com sucesso!")
    elif action == "Login":
        if dados["senha"] == senha_hash:
            st.success(f"Bem-vindo, {username}!")

            # Ações disponíveis
            st.markdown("### Ações disponíveis:")
            st.markdown("- ➕ **Adicionar valor**\n- 📊 **Ver todos os dados**\n- ➗ **Ver a soma total**\n- 📈 **Gráfico de valores**\n- 🧹 **Limpar dados**\n- 📥 **Exportar CSV**")

            acao = st.selectbox("Escolha uma ação:", ["Adicionar valor", "Ver todos os dados", "Ver a soma total", "Gráfico de valores", "Limpar dados", "Exportar CSV"])

            if acao == "Adicionar valor":
                valor = st.number_input("Digite um valor numérico para adicionar:", step=1.0)
                if st.button("Adicionar"):
                    dados["valores"].append(valor)
                    salvar_dados(dados)
                    st.success(f"Valor {valor} adicionado com sucesso!")

            elif acao == "Ver todos os dados":
                st.write("### 📋 Valores armazenados:")
                st.write(dados["valores"] if dados["valores"] else "Nenhum valor armazenado ainda.")

            elif acao == "Ver a soma total":
                total = sum(dados["valores"])
                st.metric("🔢 Soma total dos dados:", total)

            elif acao == "Gráfico de valores":
                if dados["valores"]:
                    st.line_chart(pd.DataFrame(dados["valores"], columns=["Valores"]))
                else:
                    st.info("Nenhum dado para exibir o gráfico.")

            elif acao == "Limpar dados":
                if st.button("Confirmar limpeza dos dados"):
                    dados["valores"] = []
                    salvar_dados(dados)
                    st.success("Todos os dados foram removidos.")

            elif acao == "Exportar CSV":
                if dados["valores"]:
                    df = pd.DataFrame(dados["valores"], columns=["Valores"])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV", csv, f"{username}_valores.csv", "text/csv")
                else:
                    st.info("Nenhum dado para exportar.")
        else:
            st.sidebar.error("Usuário ou senha incorretos.")
