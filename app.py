import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Atleta 35+", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# CONFIGURAÇÃO CONECTORA DO GOOGLE SHEETS
# ==========================================
# Link da sua planilha do Google Sheets
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1_JvyORAjiFa5DzhB2-VOvb0QTbWOZmX2hbOnaHShumE/edit?usp=sharing"

def carregar_dados():
    """Lê os dados em tempo real convertidos em CSV da planilha pública"""
    try:
        df_sheets = pd.read_csv(URL_PLANILHA, keep_default_na=False)
        # Garante a tipagem correta para evitar erros nos gráficos
        df_sheets["Peso"] = pd.to_numeric(df_sheets["Peso"], errors='coerce').fillna(81.2)
        df_sheets["Sono"] = pd.to_numeric(df_sheets["Sono"], errors='coerce').fillna(6.0)
        df_sheets["Energia"] = pd.to_numeric(df_sheets["Energia"], errors='coerce').fillna(3)
        df_sheets["Dor_Lombar"] = pd.to_numeric(df_sheets["Dor_Lombar"], errors='coerce').fillna(0)
        df_sheets["Km_Corrida"] = pd.to_numeric(df_sheets["Km_Corrida"], errors='coerce').fillna(0.0)
        df_sheets["Ritmo_Min_Km"] = pd.to_numeric(df_sheets["Ritmo_Min_Km"], errors='coerce').fillna(0.0)
        return df_sheets
    except Exception as e:
        return pd.DataFrame([
            {"Data": "2026-06-08", "Peso": 81.2, "Treino": "Sim", "Sono": 6.0, "Energia": 4, "Dor_Lombar": 0, "Agua_Copos": 8, "Km_Corrida": 2.87, "Ritmo_Min_Km": 4.12, "Tipo_Treino": "Tiros / Intervalado", "Detalhe_Treino": "Corrida: Ritmo Forte"}
        ])

def salvar_registro_no_sheets(novo_registro):
    """Envia os dados para o Sheets simulando o preenchimento do Google Forms"""
    # ⚠️ SUBSTITUA COM O SEU LINK formResponse DO PASSO 2
    URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSeKgnnhegCaBD-8uLG15xsx4iD-u5qyW3gbz13GB4mV_SFrfw/formResponse"
    
    # ⚠️ SUBSTITUA OS CODIGOS 'entry.XXXXX' COM OS SEUS CÓDIGOS REAIS DO FORMULÁRIO
    payload = {
       "entry.1904719613": novo_registro["Peso"],
        "entry.1098184531": novo_registro["Treino"],
        "entry.1747658324": novo_registro["Sono"],
        "entry.1054543016": novo_registro["Energia"],
        "entry.326847057": novo_registro["Dor_Lombar"],
        "entry.1532632996": novo_registro["Agua_Copos"],
        "entry.473002948": novo_registro["Km_Corrida"],
        "entry.713944778": novo_registro["Ritmo_Min_Km"],
        "entry.1276279786": novo_registro["Tipo_Treino"],
        "entry.884718567": novo_registro["Detalhe_Treino"]
    }
    
    try:
        resposta = requests.post(URL_FORM, data=payload)
        if resposta.status_code == 200:
            st.success("🔥 Sincronizado com o Google Sheets com sucesso!")
            # Alimenta a memória local para atualizar o app imediatamente na tela
            st.session_state.historico_local = pd.concat([st.session_state.historico_local, pd.DataFrame([novo_registro])], ignore_index=True)
        else:
            st.error(f"Erro ao enviar dados. Status do servidor Google: {resposta.status_code}")
    except Exception as e:
        st.error(f"Falha de conexão com a nuvem: {e}")

# Inicializa o estado lendo as informações direto da planilha
if 'historico_local' not in st.session_state:
    st.session_state.historico_local = carregar_dados()

df = st.session_state.historico_local
peso_atual = float(df["Peso"].iloc[-1]) if not df.empty else 81.2
km_semanal = df["Km_Corrida"].tail(7).sum() if not df.empty else 0.0
treinos_concluidos_semana = df["Treino"].tail(7).str.contains("Sim").sum() if not df.empty else 0

# 2. Dados de Contexto e Metas
HOJE = date.today()
DATA_CORRIDA = date(2026, 10, 19)
DATA_AGOSTO = date(2026, 8, 1)

DIAS_PARA_CORRIDA = (DATA_CORRIDA - HOJE).days
DIAS_PARA_AGOSTO = (DATA_AGOSTO - HOJE).days

PESO_INICIAL = 82.0
PESO_META = 75.0

# ==========================================
# NAVEGAÇÃO ENTRE ABAS VIA SIDEBAR
# ==========================================
st.sidebar.title("🎯 Menu de Performance")
aba_selecionada = st.sidebar.radio("Ir para:", [
    "🏋️ Visão Geral & Composição", 
    "📈 Evolução de Corrida (Métricas)",
    "💪 Fortalecimento & Fichas de Treino"
])

# ==========================================
# ABA 1: VISÃO GERAL & COMPOSIÇÃO
# ==========================================
if aba_selecionada == "🏋️ Visão Geral & Composição":
    st.title("⚡ Dashboard de Performance: Rumo aos 75kg")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        progresso_peso = ((PESO_INICIAL - peso_atual) / (PESO_INICIAL - PESO_META)) * 100
        st.metric(label="🏋️ Peso Atual", value=f"{peso_atual} kg", delta=f"{peso_atual - PESO_INICIAL:.1f} kg desde o início")
        st.progress(min(max(progresso_peso / 100, 0.0), 1.0), text=f"{progresso_peso:.1f}% da meta")

    with col2:
        st.metric(label="🎯 Meta de Peso (Agosto)", value=f"{PESO_META} kg", delta=f"{DIAS_PARA_AGOSTO} dias restantes", delta_color="inverse")

    with col3:
        st.metric(label="📊 Atividades (7 dias)", value=f"{treinos_concluidos_semana} sessões", delta=f"{km_semanal} km rodados")

    with col4:
        status_lombar = "⚠️ Alerta" if not df.empty and df["Dor_Lombar"].iloc[-1] >= 2 else "✅ Estável"
        st.metric(label="🛡️ Status da Lombar", value=status_lombar, delta=f"Dor atual: {df['Dor_Lombar'].iloc[-1] if not df.empty else 0}/3", delta_color="inverse")

    st.markdown("---")

    st.subheader("📝 Registro do Dia (Check-in Rápido de Rotina)")
    with st.form("registro_diario"):
        c1, c2, c3 = st.columns(3)
        with c1:
            input_peso = st.number_input("Peso de hoje (kg):", min_value=60.0, max_value=100.0, value=peso_atual, step=0.1)
            input_treino = st.selectbox("Registrar atividade genérica/outros hoje?", ["Não", "Sim"])
        with c2:
            input_sono = st.slider("Horas de Sono:", 4.0, 9.0, 6.0, step=0.5)
            input_energia = st.slider("Nível de Energia (1-5):", 1, 5, 3)
        with c3:
            input_lombar = st.slider("Incômodo na Lombar (0-3):", 0, 3, 0)
            input_agua = st.number_input("Copos de água:", min_value=0, max_value=20, value=6)
        
        botao_salvar = st.form_submit_button("Salvar Registro de Rotina")

    if botao_salvar:
        novo_registro = {
            "Data": str(HOJE), "Peso": input_peso, "Treino": input_treino, 
            "Sono": input_sono, "Energia": input_energia, "Dor_Lombar": input_lombar, 
            "Agua_Copos": input_agua, "Km_Corrida": 0.0, "Ritmo_Min_Km": 0.0, "Tipo_Treino": "Nenhum", "Detalhe_Treino": "Registro Diário"
        }
        salvar_registro_no_sheets(novo_registro)
        st.rerun()

    st.markdown("---")
    st.subheader("📊 Gráficos de Evolução Muscular e Resiliência")
    
    if not df.empty:
        g1, g2 = st.columns(2)
        with g1:
            fig_peso = px.line(df, x="Data", y="Peso", title="Tendência do Peso (Rumo aos 75kg)", markers=True)
            fig_peso.update_traces(line_color='#FF4B4B', line_width=3)
            st.plotly_chart(fig_peso, use_container_width=True)
        with g2:
            fig_treino = px.histogram(df, x="Data", y="Treino", color="Treino", title="Histórico de Atividade (Constância Geral)", color_discrete_map={"Sim": "#4CAF50", "Não": "#F44336"})
            st.plotly_chart(fig_treino, use_container_width=True)

# ==========================================
# ABA 2: EVOLUÇÃO DE CORRIDA (MÉTRICAS)
# ==========================================
elif aba_selecionada == "📈 Evolução de Corrida (Métricas)":
    st.title("🏃‍♂️ Histórico de Performance: Meia Maratona")
    st.info(f"🏁 Faltam exatamente **{DIAS_PARA_CORRIDA} dias** para a prova (19 de Outubro).")
    st.markdown("---")

    cx1, cx2, cx3 = st.columns(3)
    with cx1:
        st.metric(label="📈 Volume Acumulado nos Últimos 7 dias", value=f"{km_semanal} km")
    with cx2:
        maior_longo = df["Km_Corrida"].max() if not df.empty else 0.0
        st.metric(label="🚀 Maior Longo Registrado", value=f"{maior_longo} km")
    with cx3:
        ritmos_validos = df[df["Ritmo_Min_Km"] > 0]["Ritmo_Min_Km"] if not df.empty else pd.Series()
        melhor_ritmo = ritmos_validos.min() if not ritmos_validos.empty else 0.0
        st.metric(label="⚡ Melhor Ritmo Registrado", value=f"{melhor_ritmo:.2f} min/km")

    st.markdown("---")
    st.subheader("📈 Progressão de Carga Realizada (Volume vs Ritmo)")
    df_corridas = df[df["Km_Corrida"] > 0] if not df.empty else pd.DataFrame()
    
    if not df_corridas.empty:
        fig_corrida = px.scatter(df_corridas, x="Data", y="Km_Corrida", size="Km_Corrida", color="Ritmo_Min_Km",
                                 title="Análise de Treinos de Corrida Registrados",
                                 hover_data=["Tipo_Treino", "Ritmo_Min_Km"],
                                 color_continuous_scale=px.colors.sequential.Sunset_r)
        st.plotly_chart(fig_corrida, use_container_width=True)
    else:
        st.warning("Nenhum treino de corrida registrado.")

# ==========================================
# ABA 3: FORTALECIMENTO & FICHAS DE TREINO
# ==========================================
else:
    st.title("💪 Prescrição de Treinos: Calistenia & Corrida")
    st.markdown("---")

    st.subheader("✅ Central de Conclusão Diária (Registrar Treino)")
    with st.form("central_registro_treinos"):
        tipo_registro = st.radio("O que você treinou hoje?", ["Calistenia: TREINO A (Empurrar + Pernas)", "Calistenia: TREINO B (Puxar + Core Seguro)", "Corrida (Planilha de Meia Maratona)"])
        
        c_cor1, c_cor2, c_cor3 = st.columns(3)
        with c_cor1:
            km_rodados = st.number_input("Se foi corrida, quantos km? (Distância):", min_value=0.0, max_value=42.0, value=0.0, step=0.1)
        with c_cor2:
            ritmo_corrida = st.number_input("Se foi corrida, qual o Pace médio? (min/km):", min_value=0.0, max_value=10.0, value=0.0, step=0.01, format="%.2f")
        with c_cor3:
            estilo_corrida = st.selectbox("Se foi corrida, qual o tipo de estímulo?", ["Nenhum / Calistenia", "Tiros / Intervalado", "Tempo Run (Ritmo Prova)", "Longo Progressivo", "Regenerativo"])
            
        botao_gravar_tudo = st.form_submit_button("💾 Gravar Atividade Concluída")

    if botao_gravar_tudo:
        if "Calistenia" in tipo_registro:
            detalhe_final = "Treino A Concluído" if "TREINO A" in tipo_registro else "Treino B Concluído"
            nova_linha = {
                "Data": str(HOJE), "Peso": peso_atual, "Treino": "Sim", 
                "Sono": df["Sono"].iloc[-1] if not df.empty else 6.0, 
                "Energia": df["Energia"].iloc[-1] if not df.empty else 3, 
                "Dor_Lombar": df["Dor_Lombar"].iloc[-1] if not df.empty else 0, 
                "Agua_Copos": df["Agua_Copos"].iloc[-1] if not df.empty else 6, 
                "Km_Corrida": 0.0, "Ritmo_Min_Km": 0.0, "Tipo_Treino": "Nenhum", "Detalhe_Treino": detalhe_final
            }
        else:
            nova_linha = {
                "Data": str(HOJE), "Peso": peso_atual, "Treino": "Sim", 
                "Sono": df["Sono"].iloc[-1] if not df.empty else 6.0, 
                "Energia": df["Energia"].iloc[-1] if not df.empty else 3, 
                "Dor_Lombar": df["Dor_Lombar"].iloc[-1] if not df.empty else 0, 
                "Agua_Copos": df["Agua_Copos"].iloc[-1] if not df.empty else 6, 
                "Km_Corrida": km_rodados, "Ritmo_Min_Km": ritmo_corrida, "Tipo_Treino": estilo_corrida, "Detalhe_Treino": f"Corrida: {estilo_corrida}"
            }
            
        salvar_registro_no_sheets(nova_linha)
        st.rerun()

    st.markdown("---")
    
  
    # Abas Visuais contendo as Fichas Técnicas
    aba_corrida, aba_treino_a, aba_treino_b, aba_mobilidade = st.tabs([
        "🏃‍♂️ PLANILHA DE CORRIDA (2x/Semana)", 
        "🔥 CALISTENIA: TREINO A", 
        "🧬 CALISTENIA: TREINO B", 
        "🧘 MOBILIDADE & ALONGAMENTO"
    ])

    with aba_corrida:
        st.markdown("### 📋 Planejamento de Corrida Rumo aos 21km (19 de Outubro)")
        st.warning("🎯 **Zonas de Ritmo Calculadas:** Confortável (05:15~05:45) | Ritmo de Prova (04:55~05:10) | Tiro (04:05~04:20)")
        
        st.markdown("#### **Fase 1: Base e Adaptação (Junho e Julho)**")
        st.markdown("""
        * **Sessão 1 (Meio da semana):** Intervalado. 2km aquecimento + 4 a 6 tiros de 1.000m (Ritmo de Tiro) com 2 min de descanso caminhando.
        * **Sessão 2 (Fim de semana):** O Longo Progressivo.
            * *Semanas 1 e 2:* **10 km** (Ritmo Confortável)
            * *Semanas 3 e 4:* **12 km** (Ritmo Confortável)
            * *Semanas 5 e 6:* **14 km** (Últimos 2km no Ritmo de Prova)
        """)
        
        st.markdown("#### **Fase 2: Resistência Específica (Agosto e Setembro)**")
        st.markdown("""
        * **Sessão 1 (Meio da semana):** Tempo Run. 2km aquecimento + 6km a 8km contínuos no Ritmo de Prova + 1km desaquecimento.
        * **Sessão 2 (Fim de semana):** O Longo Alvo.
            * *Semanas 7 e 8:* **15 km** (Últimos 3km no Ritmo de Prova)
            * *Semanas 9 e 10:* **17 km** (Ritmo Confortável)
            * *Semanas 11 e 12:* **19 km** (Ápice do volume. Teste oficial de gel de carboidrato)
        """)
        
        st.markdown("#### **Fase 3: Polimento e Prova (Outubro)**")
        st.markdown("""
        * **Semana 13 (Duas semanas antes):** * Sessão 1: 5km Confortável + 4 tiros de 400m rápidos.
            * Sessão 2: **12 km** no Ritmo de Prova.
        * **Semana 14 (Semana da Prova):**
            * Sessão 1 (Terça): 5km regenerativos bem leves para tirar a ansiedade.
            * **DOMINGO 19/10:** 🏁 **Grande Dia - Meia Maratona (21.097m)!**
        """)

    with aba_treino_a:
        st.markdown("### 🥊 Foco: Peito, Ombros, Tríceps e Coxas")
        st.caption("Método Bi-set: Faça o exercício 1, vá direto para o 2, descanse 60s. Repita as séries.")
        st.error("**Bloco 1: Força Base (3 a 4 Séries)**")
        st.markdown("""
        * **Exercício 1:** Flexões de Braço Tradicionais — *12 a 15 repetições*
        * **Exercício 2:** Agachamento Livre (Até 90°, preservando a curvatura lombar) — *15 a 20 repetições*
        """)
        st.warning("**Bloco 2: Resistência & Estabilidade da Passada (3 Séries)**")
        st.markdown("""
        * **Exercício 1:** Flexões com Mãos Elevadas (Banco/Sofá) — *Cadência veloz, 10 a 12 repetições*
        * **Exercício 2:** Afundo Estático (Passada) — *10 repetições completas por perna*
        """)

    with aba_treino_b:
        st.markdown("### 🧬 Foco: Costas, Bíceps e Fortalecimento de Cadeia Posterior")
        st.caption("Método Bi-set: Faça o exercício 1, vá direto para o 2, descanse 60s. Repita as séries.")
        st.error("**Bloco 1: Cadeia Posterior e Costas (3 a 4 Séries)**")
        st.markdown("""
        * **Exercício 1:** Barra Australiana (Debaixo da mesa) OU Remada com Toalha na Porta — *10 a 12 repetições*
        * **Exercício 2:** Elevação de Quadril / Ponte de Glúteo — *15 repetições conscientes (Glúteo firme estabiliza a coluna)*
        """)
        st.warning("**Bloco 2: Core Estrutural & Antilesão (3 Séries)**")
        st.markdown("""
        * **Exercício 1:** Prancha Frontal Isométrica — *30 a 45 segundos travado*
        * **Exercício 2:** Perdigueiro Intercalado (Bird-Dog) — *10 repetições alternadas (Padrão ouro fisioterapêutico)*
        """)

    with aba_mobilidade:
        st.markdown("### 🚨 Rotina Obrigatória de Proteção Articular (3 a 4 min)")
        st.info("Foco primário: Soltar articulação coxo-femoral e descomprimir a região lombar.")
        st.markdown("""
        1. **Gato / Camelo (Cat-Cow):** 10 repetições controladas.
        2. **Alongamento do Flexor de Quadril:** 30 segundos sustentados para cada lado (Alivia a tensão lombar de ficar sentado).
        3. **Rotação de Tronco em 4 Apoios:** 8 repetições dinâmicas para cada lado.
        """)
        st.markdown("---")
        st.markdown("### 💤 Desaceleração Final (2 min)")
        st.markdown("""
        * **Postura da Criança (Child's Pose):** 1 minuto mantendo os braços esticados à frente.
        * **Alongamento de Posteriores (Sentado):** 1 minuto buscando a canela ou ponta dos pés.
        """)
