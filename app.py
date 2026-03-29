import streamlit as st
import yfinance as yf
import pandas as pd
import math
from datetime import datetime

# ====================== CONFIG ======================
st.set_page_config(page_title="Étude Sharpe Ratio", page_icon="📊", layout="wide")
st.markdown("""
    <style>
        .main-header {font-size: 2.5rem; font-weight: bold; color: #1E88E5;}
        .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;}
        .stDataFrame {border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Étude de Performance Boursière")
st.markdown("**Ratio de Sharpe** — Le meilleur outil pour comparer rendement et risque")

st.sidebar.header("🔧 Paramètres")

# ====================== DICTIONNAIRE ======================
tickers_dict = {
    'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', 'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.', 'TSLA': 'Tesla Inc.', 'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.', 'NFLX': 'Netflix Inc.',
    'MC.PA': 'LVMH', 'TTE.PA': 'TotalEnergies', 'HO.PA': 'Thales',
    'AI.PA': 'Air Liquide', 'BNP.PA': 'BNP Paribas', 'RMS.PA': 'Hermès',
    'VIE.PA': 'Veolia', 'BABA': 'Alibaba Group',
}

# ====================== SESSION STATE ======================
if "selected_formatted" not in st.session_state:
    st.session_state.selected_formatted = [
        "AAPL - Apple Inc.", "MSFT - Microsoft Corporation",
        "MC.PA - LVMH", "TSLA - Tesla Inc."
    ]

# ====================== SIDEBAR ======================
st.sidebar.subheader("1️⃣ Sélection des actions")

search_term = st.sidebar.text_input(
    "🔎 Rechercher une action",
    placeholder="NVIDIA, LVMH, Total..."
)

if search_term:
    filtered = {t: n for t, n in tickers_dict.items() 
                if search_term.lower() in t.lower() or search_term.lower() in n.lower()}
else:
    filtered = tickers_dict

options = [f"{t} - {n}" for t, n in filtered.items()]

# Inclusion forcée des sélections actuelles
for item in st.session_state.selected_formatted:
    if item not in options:
        options.append(item)
options = list(dict.fromkeys(options))

selected_formatted = st.sidebar.multiselect(
    "Actions sélectionnées",
    options=options,
    default=st.session_state.selected_formatted,
    help="Tu peux sélectionner plusieurs actions"
)
st.session_state.selected_formatted = selected_formatted
selected_tickers = [item.split(" - ")[0] for item in selected_formatted]

st.sidebar.subheader("2️⃣ Période d'analyse")
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Début", value=datetime(2019, 1, 1))
end_date = col2.date_input("Fin", value=datetime.today())

st.sidebar.subheader("3️⃣ Taux sans risque")
risk_free_rate = st.sidebar.number_input(
    "Taux sans risque (%)",
    value=2.0,
    step=0.1,
    help="Taux par défaut = 2 % (équivalent à un bon placement sans risque)"
) / 100

# ====================== LANCEMENT ======================
if st.button("🚀 Lancer l'analyse Sharpe", type="primary", use_container_width=True):
    if not selected_tickers:
        st.error("Sélectionne au moins une action !")
    else:
        with st.spinner("📡 Récupération des cours sur Yahoo Finance..."):
            data = yf.download(
                selected_tickers,
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False
            )['Adj Close']

        if isinstance(data, pd.Series):
            data = data.to_frame(name=selected_tickers[0])

        if data.empty:
            st.error("Aucune donnée trouvée. Vérifie les dates ou les tickers.")
        else:
            # ====================== CALCULS ======================
            returns = data.pct_change().dropna()
            vol_ann = returns.std() * math.sqrt(252)
            cum_ret = (data.iloc[-1] / data.iloc[0]) - 1
            years = (data.index[-1] - data.index[0]).days / 365.25
            ann_ret = (1 + cum_ret) ** (1 / years) - 1
            sharpe = (ann_ret - risk_free_rate) / vol_ann

            results = pd.DataFrame({
                "Rendement Annualisé": ann_ret,
                "Volatilité Annualisée": vol_ann,
                "Ratio de Sharpe": sharpe,
                "Rendement Cumulé": cum_ret
            }).round(4)

            # ====================== TABS ======================
            tab1, tab2, tab3 = st.tabs(["📋 Résultats", "📈 Graphiques", "📊 Données brutes"])

            with tab1:
                # KPI Cards
                col_a, col_b, col_c = st.columns(3)
                best = results["Ratio de Sharpe"].max()
                avg = results["Ratio de Sharpe"].mean()
                worst = results["Ratio de Sharpe"].min()

                col_a.metric("🏆 Meilleur Sharpe", f"{best:.3f}", delta="Top performer")
                col_b.metric("📊 Sharpe moyen", f"{avg:.3f}")
                col_c.metric("⚠️ Plus faible Sharpe", f"{worst:.3f}")

                st.subheader("Classement complet")
                styled_results = results.style.background_gradient(
                    subset=["Ratio de Sharpe"], cmap="RdYlGn"
                ).format("{:.4f}")
                st.dataframe(styled_results, use_container_width=True)

                st.download_button(
                    label="📥 Télécharger le tableau en CSV",
                    data=results.to_csv().encode("utf-8"),
                    file_name=f"sharpe_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                with st.expander("📌 Comment est calculé le Ratio de Sharpe ?"):
                    st.markdown("""
                    **Formule :**  
                    Sharpe = (Rendement annualisé − Taux sans risque) / Volatilité annualisée  
                    Plus le ratio est élevé, **meilleur** est le couple rendement/risque.
                    """)

            with tab2:
                st.subheader("Évolution des rendements cumulés")
                cum_returns = (1 + returns).cumprod() - 1
                st.line_chart(cum_returns, use_container_width=True)

                st.subheader("Ratio de Sharpe par action")
                st.bar_chart(results["Ratio de Sharpe"].sort_values(ascending=False))

            with tab3:
                st.subheader("Prix ajustés (Adj Close)")
                st.dataframe(data.round(2), use_container_width=True)

            st.success(f"✅ Analyse terminée pour la période du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')} !")

else:
    # Écran d'accueil quand rien n’est lancé
    st.info("👈 Remplis la barre latérale et clique sur **Lancer l'analyse** pour commencer.")
    st.markdown("""
    **Cette application te permet de :**
    - Comparer le ratio de Sharpe de plusieurs actions
    - Choisir tes propres dates et ton taux sans risque
    - Voir instantanément quelles actions sont les plus efficaces (rendement/risque)
    """)

st.caption("Made with ❤️ by [bahEzope224](https://github.com/bahEzope224)")