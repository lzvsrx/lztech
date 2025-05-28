import streamlit as st
import datetime
import json
import os
import pandas as pd
import hashlib
import matplotlib.pyplot as plt # Importar matplotlib para o gráfico de histograma

# Função para criptografar senha
def hash_password(password):
    """Criptografa a senha usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# Caminho base dos dados do usuário
# Em um ambiente de produção (como o Streamlit Community Cloud),
# este diretório pode precisar de permissões de escrita ou ser substituído
# por um banco de dados persistente (ex: Firestore, PostgreSQL).
DATA_DIR = "dados_usuarios"
os.makedirs(DATA_DIR, exist_ok=True)

# Configuração da página e mensagem de boas-vindas
st.set_page_config(page_title="LZTech Chatbot", layout="centered")
st.markdown(f"# 🤖 Bem-vindo ao LZTech\n📅 Data: {datetime.datetime.now().strftime('%d/%m/%Y')}")

# Seção de Autenticação na barra lateral
st.sidebar.header("🔐 Login ou Cadastro")
username = st.sidebar.text_input("Usuário")
password = st.sidebar.text_input("Senha", type="password")
action = st.sidebar.radio("Ação", ["Login", "Cadastrar"])

# Define o caminho do arquivo JSON para o usuário atual
user_file = os.path.join(DATA_DIR, f"{username}.json")

# Função para carregar dados do usuário
def carregar_dados():
    """
    Carrega os dados do usuário de um arquivo JSON.
    Retorna um dicionário padrão se o arquivo não existir.
    Converte entradas antigas (apenas números) para o novo formato de dicionário.
    """
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Verifica se a chave 'valores' existe e se é uma lista
                if "valores" in dados and isinstance(dados["valores"], list):
                    # Converte entradas antigas (apenas números) para o novo formato
                    novos_valores = []
                    for item in dados["valores"]:
                        if isinstance(item, (int, float)):
                            # Se for um número, converte para o novo formato com valores padrão
                            novos_valores.append({
                                "valor": item,
                                "tipo_atividade": "Não especificado",
                                "data": "Data desconhecida"
                            })
                        elif isinstance(item, dict):
                            # Se já for um dicionário, garante que todas as chaves existem
                            # e adiciona padrões se estiverem faltando
                            novos_valores.append({
                                "valor": item.get("valor", 0.0),
                                "tipo_atividade": item.get("tipo_atividade", "Não especificado"),
                                "data": item.get("data", "Data desconhecida")
                            })
                        else:
                            # Lida com tipos inesperados, talvez ignorando ou registrando um erro
                            st.warning(f"Tipo de dado inesperado encontrado: {type(item)}. Ignorando.")
                    dados["valores"] = novos_valores
                else:
                    # Se 'valores' não existir ou não for uma lista, inicializa
                    dados["valores"] = []
                return dados
        except json.JSONDecodeError:
            st.error(f"Erro ao ler o arquivo de dados para {username}. Criando um novo.")
            return {"senha": "", "valores": []}
    else:
        return {"senha": "", "valores": []}

# Função para salvar dados do usuário
def salvar_dados(dados):
    """Salva os dados do usuário em um arquivo JSON."""
    try:
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4) # Adiciona indentação para melhor legibilidade
    except IOError as e:
        st.error(f"Erro ao salvar dados para {username}: {e}")

# Lógica de Login ou Cadastro
if username and password:
    dados = carregar_dados()
    senha_hash = hash_password(password)

    if action == "Cadastrar":
        if os.path.exists(user_file) and dados["senha"] != "":
            # Verifica se o arquivo existe e se já tem uma senha definida (indicando usuário existente)
            st.sidebar.warning("Usuário já existe.")
        else:
            dados["senha"] = senha_hash
            salvar_dados(dados)
            st.sidebar.success("Cadastro realizado com sucesso!")
            st.info("Por favor, faça login com seu novo usuário e senha.")
    elif action == "Login":
        if dados["senha"] == senha_hash and dados["senha"] != "":
            st.success(f"Bem-vindo, {username}!")

            # Ações disponíveis após o login
            st.markdown("### Ações disponíveis:")
            st.markdown("- ➕ **Adicionar valor**\n- 📊 **Ver todos os dados**\n- ➗ **Ver a soma total**\n- 📈 **Gráfico de valores**\n- 🧹 **Limpar dados**\n- 📥 **Exportar CSV**")

            acao = st.selectbox("Escolha uma ação:", ["Adicionar valor", "Ver todos os dados", "Ver a soma total", "Gráfico de valores", "Limpar dados", "Exportar CSV"])

            if acao == "Adicionar valor":
                valor = st.number_input("Digite um valor numérico para adicionar:", step=1.0, format="%.2f")
                tipo_atividade = st.text_input("Tipo de atividade (ex: Compras, Salário, Lazer):")
                data_atividade = st.date_input("Data da atividade:", datetime.date.today())

                if st.button("Adicionar"):
                    # Adiciona um dicionário com valor, tipo de atividade e data
                    dados["valores"].append({
                        "valor": valor,
                        "tipo_atividade": tipo_atividade,
                        "data": data_atividade.strftime("%Y-%m-%d") # Formata a data para string
                    })
                    salvar_dados(dados)
                    st.success(f"Valor {valor} de '{tipo_atividade}' em {data_atividade.strftime('%d/%m/%Y')} adicionado com sucesso!")

            elif acao == "Ver todos os dados":
                st.write("### 📋 Valores armazenados:")
                if dados["valores"]:
                    # Cria um DataFrame a partir da lista de dicionários
                    df_valores = pd.DataFrame(dados["valores"])
                    st.dataframe(df_valores)
                else:
                    st.info("Nenhum valor armazenado ainda.")

            elif acao == "Ver a soma total":
                # Calcula a soma apenas dos valores numéricos
                total = sum([item["valor"] for item in dados["valores"]]) if dados["valores"] else 0
                st.metric("🔢 Soma total dos dados:", total)

            elif acao == "Gráfico de valores":
                if dados["valores"]:
                    # Extrai apenas os valores numéricos para o gráfico de linha
                    valores_numericos = [item["valor"] for item in dados["valores"]]
                    df_grafico = pd.DataFrame(valores_numericos, columns=["Valores"])
                    st.line_chart(df_grafico)
                    st.markdown("---")
                    st.write("### Distribuição dos Valores")
                    fig, ax = plt.subplots()
                    ax.hist(valores_numericos, bins=5, edgecolor='black') # Usa os valores numéricos
                    ax.set_title('Distribuição dos Valores')
                    ax.set_xlabel('Valor')
                    ax.set_ylabel('Frequência')
                    st.pyplot(fig)
                else:
                    st.info("Nenhum dado para exibir o gráfico.")

            elif acao == "Limpar dados":
                st.warning("Esta ação removerá todos os seus dados. Tem certeza?")
                if st.button("Confirmar limpeza dos dados"):
                    dados["valores"] = []
                    salvar_dados(dados)
                    st.success("Todos os dados foram removidos.")

            elif acao == "Exportar CSV":
                if dados["valores"]:
                    # Cria um DataFrame a partir da lista de dicionários para exportação
                    df = pd.DataFrame(dados["valores"])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV", csv, f"{username}_valores.csv", "text/csv")
                else:
                    st.info("Nenhum dado para exportar.")
        else:
            st.sidebar.error("Usuário ou senha incorretos, ou usuário não cadastrado.")
elif username or password: # Se um dos campos estiver preenchido, mas não ambos
    st.sidebar.info("Por favor, preencha ambos os campos de usuário e senha.")
else: # Se nenhum campo estiver preenchido
    st.sidebar.info("Digite seu usuário e senha para fazer login ou cadastrar-se.")
