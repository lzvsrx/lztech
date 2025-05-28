import streamlit as st
import datetime
import json
import os
import pandas as pd
import hashlib
import matplotlib.pyplot as plt # Importar matplotlib para o gráfico de histograma

# --- Funções de Utilitário ---

def hash_password(password):
    """Criptografa a senha usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# --- Configuração do Diretório de Dados ---

# Onde os arquivos JSON dos usuários serão armazenados.
# Para deploy na nuvem (ex: Streamlit Community Cloud), considere
# usar um banco de dados persistente (ex: Firestore, PostgreSQL)
# ou ajustar permissões de escrita se o ambiente for restrito.
DATA_DIR = "dados_usuarios"
os.makedirs(DATA_DIR, exist_ok=True) # Cria o diretório se não existir

# --- Funções de Manipulação de Dados do Usuário ---

def carregar_dados(username):
    """
    Carrega os dados de um usuário de um arquivo JSON.
    Inicializa um dicionário padrão se o arquivo não existir ou estiver corrompido.
    Realiza a migração de formatos de dados antigos (apenas números) para o novo formato
    (dicionários com valor, tipo_atividade e data).
    """
    user_file = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Garante que 'valores' é uma lista e contém os campos esperados
                if "valores" not in dados or not isinstance(dados["valores"], list):
                    dados["valores"] = [] # Inicializa se ausente ou tipo incorreto

                novos_valores = []
                for item in dados["valores"]:
                    if isinstance(item, (int, float)):
                        # Migra formato antigo (apenas número) para o novo formato
                        novos_valores.append({
                            "valor": item,
                            "tipo_atividade": "Não especificado",
                            "data": "Desconhecida" # Usar string para datas antigas
                        })
                    elif isinstance(item, dict):
                        # Garante que todos os campos necessários estão presentes no dicionário
                        # e adiciona padrões se estiverem faltando
                        novos_valores.append({
                            "valor": item.get("valor", 0.0),
                            "tipo_atividade": item.get("tipo_atividade", "Não especificado"),
                            "data": item.get("data", "Desconhecida")
                        })
                    else:
                        st.warning(f"Tipo de dado inesperado encontrado para '{username}': {type(item)}. Ignorando entrada.")
                dados["valores"] = novos_valores
                return dados
        except json.JSONDecodeError:
            st.error(f"Erro ao ler o arquivo de dados para '{username}'. Criando um novo arquivo de dados.")
            return {"senha": "", "valores": []}
    else:
        return {"senha": "", "valores": []}

def salvar_dados(username, dados):
    """Salva os dados do usuário em um arquivo JSON."""
    user_file = os.path.join(DATA_DIR, f"{username}.json")
    try:
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4) # Adiciona indentação para legibilidade
    except IOError as e:
        st.error(f"Erro ao salvar dados para '{username}': {e}")

# --- Configuração da Página Streamlit ---

st.set_page_config(page_title="LZTech Chatbot", layout="centered")
st.markdown(f"# 🤖 Bem-vindo ao LZTech\n📅 Data: {datetime.datetime.now().strftime('%d/%m/%Y')}")

# --- Seção de Autenticação na Barra Lateral ---

st.sidebar.header("🔐 Login ou Cadastro")
username_input = st.sidebar.text_input("Usuário", key="username_auth")
password_input = st.sidebar.text_input("Senha", type="password", key="password_auth")
action_auth = st.sidebar.radio("Ação", ["Login", "Cadastrar"], key="action_auth")

# --- Lógica de Autenticação e Ações Pós-Login ---

# Variável de estado para controlar se o usuário está logado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_username" not in st.session_state:
    st.session_state.current_username = ""

if username_input and password_input:
    dados_usuario = carregar_dados(username_input)
    senha_hash_input = hash_password(password_input)

    if action_auth == "Cadastrar":
        if os.path.exists(os.path.join(DATA_DIR, f"{username_input}.json")) and dados_usuario["senha"] != "":
            st.sidebar.warning("Usuário já existe. Por favor, escolha outro nome de usuário ou faça login.")
        else:
            dados_usuario["senha"] = senha_hash_input
            salvar_dados(username_input, dados_usuario)
            st.sidebar.success("Cadastro realizado com sucesso! Agora faça login.")
            st.info("Usuário cadastrado com sucesso. Por favor, use suas credenciais para fazer login.")
            # Limpar campos para evitar login automático após cadastro
            st.session_state.logged_in = False
            st.session_state.current_username = ""
    elif action_auth == "Login":
        if dados_usuario["senha"] == senha_hash_input and dados_usuario["senha"] != "":
            st.session_state.logged_in = True
            st.session_state.current_username = username_input
            st.sidebar.success(f"Login bem-sucedido! Bem-vindo(a), {username_input}!")
        else:
            st.sidebar.error("Usuário ou senha incorretos, ou usuário não cadastrado.")
            st.session_state.logged_in = False
            st.session_state.current_username = ""
else:
    if not st.session_state.logged_in:
        st.sidebar.info("Digite seu usuário e senha para fazer login ou cadastrar-se.")

# --- Conteúdo Principal Após o Login ---

if st.session_state.logged_in:
    st.markdown(f"## Olá, {st.session_state.current_username}!")
    st.markdown("### Ações disponíveis:")
    st.markdown("- ➕ **Adicionar valor**\n- 📊 **Ver todos os dados**\n- ➗ **Ver a soma total**\n- 📈 **Gráfico de valores**\n- 🧹 **Limpar dados**\n- 📥 **Exportar CSV**")

    # Recarregar dados do usuário logado
    current_user_data = carregar_dados(st.session_state.current_username)

    acao = st.selectbox("Escolha uma ação:",
                        ["Adicionar valor", "Ver todos os dados", "Ver a soma total",
                         "Gráfico de valores", "Limpar dados", "Exportar CSV"],
                        key="main_action_select")

    if acao == "Adicionar valor":
        st.markdown("---")
        st.write("### Adicionar Novo Valor")
        with st.form("adicionar_valor_form"):
            valor = st.number_input("Digite um valor numérico:", step=0.01, format="%.2f")
            tipo_atividade = st.text_input("Tipo de atividade (ex: Compras, Salário, Lazer):")
            data_atividade = st.date_input("Data da atividade:", datetime.date.today())

            submitted = st.form_submit_button("Adicionar Valor")
            if submitted:
                if valor is not None:
                    # Adiciona um dicionário com valor, tipo de atividade e data
                    current_user_data["valores"].append({
                        "valor": valor,
                        "tipo_atividade": tipo_atividade if tipo_atividade else "Não especificado", # Garante um valor padrão
                        "data": data_atividade.strftime("%Y-%m-%d") # Formata a data para string padrão
                    })
                    salvar_dados(st.session_state.current_username, current_user_data)
                    st.success(f"Valor **{valor:.2f}** (Tipo: **{tipo_atividade if tipo_atividade else 'Não especificado'}**) em **{data_atividade.strftime('%d/%m/%Y')}** adicionado com sucesso!")
                else:
                    st.error("Por favor, digite um valor numérico.")

    elif acao == "Ver todos os dados":
        st.markdown("---")
        st.write("### 📋 Valores Armazenados:")
        if current_user_data["valores"]:
            # Cria um DataFrame a partir da lista de dicionários
            df_valores = pd.DataFrame(current_user_data["valores"])
            # Reorganiza as colunas para melhor visualização
            df_valores = df_valores[["data", "tipo_atividade", "valor"]]
            st.dataframe(df_valores, use_container_width=True)
        else:
            st.info("Nenhum valor armazenado ainda. Adicione alguns valores!")

    elif acao == "Ver a soma total":
        st.markdown("---")
        # Calcula a soma apenas dos valores numéricos
        total = sum([item["valor"] for item in current_user_data["valores"]]) if current_user_data["valores"] else 0
        st.metric("🔢 Soma total dos dados:", f"R$ {total:.2f}")

    elif acao == "Gráfico de valores":
        st.markdown("---")
        if current_user_data["valores"]:
            # Extrai apenas os valores numéricos para o gráfico de linha
            valores_numericos = [item["valor"] for item in current_user_data["valores"]]
            if valores_numericos: # Verifica se há valores após a extração
                st.write("### Tendência dos Valores ao longo do tempo")
                # Cria DataFrame com índices para simular tempo
                df_grafico = pd.DataFrame(valores_numericos, columns=["Valores"])
                st.line_chart(df_grafico)

                st.markdown("---")
                st.write("### Distribuição dos Valores")
                fig, ax = plt.subplots()
                ax.hist(valores_numericos, bins=len(set(valores_numericos)) if len(set(valores_numericos)) < 10 else 10, edgecolor='black') # Ajusta bins
                ax.set_title('Distribuição dos Valores')
                ax.set_xlabel('Valor')
                ax.set_ylabel('Frequência')
                st.pyplot(fig)
            else:
                st.info("Nenhum dado numérico para exibir o gráfico.")
        else:
            st.info("Nenhum dado para exibir o gráfico. Adicione alguns valores primeiro!")

    elif acao == "Limpar dados":
        st.markdown("---")
        st.warning("Esta ação removerá **TODOS** os seus dados armazenados. Tem certeza?")
        if st.button("Sim, Confirmar limpeza dos dados"):
            current_user_data["valores"] = []
            salvar_dados(st.session_state.current_username, current_user_data)
            st.success("Todos os seus dados foram removidos com sucesso.")

    elif acao == "Exportar CSV":
        st.markdown("---")
        if current_user_data["valores"]:
            # Cria um DataFrame a partir da lista de dicionários para exportação
            df_export = pd.DataFrame(current_user_data["valores"])
            # Garante a ordem das colunas para o CSV
            df_export = df_export[["data", "tipo_atividade", "valor"]]
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Dados como CSV",
                data=csv,
                file_name=f"{st.session_state.current_username}_valores.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhum dado para exportar. Adicione alguns valores primeiro!")

    # --- Botão de Logout ---
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair (Logout)", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.current_username = ""
        st.rerun() # Recarrega a página para resetar o estado


else:
    # Mensagem se o usuário não estiver logado
    st.markdown("---")
    st.info("Por favor, faça login ou cadastre-se na barra lateral para acessar as funcionalidades.")

