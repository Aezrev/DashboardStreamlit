import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="Steam Games Dashboard", layout="wide")
st.title("Steam Games Dashboard")  # Titlu dashboard

# ── Încărcare fișier CSV ─────────────────────────────
fisier = st.file_uploader("Încarcă fișierul CSV", type=["csv"])

if fisier is None:
    st.info("Încarcă un fișier CSV pentru a continua.")
    st.stop()

df = pd.read_csv(fisier)
df.columns = df.columns.str.strip()  # curăță spațiile din numele coloanelor

st.write("Numele coloanelor din CSV:", df.columns.tolist())  # pentru debugging

# ── Detectare automată coloană de preț ─────────────
pret_col = [col for col in df.columns if 'price' in col.lower()]
if pret_col:
    pret_col = pret_col[0]
    df[pret_col] = pd.to_numeric(df[pret_col], errors='coerce')  # transformă non-numeric în NaN
else:
    pret_col = None

# ── Statistici generale ──────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total jocuri", len(df))
col2.metric("Număr coloane", len(df.columns))

if pret_col:
    col3.metric("Preț mediu", f"${df[pret_col].mean():.2f}")
else:
    col3.metric("Preț mediu", "N/A")

st.dataframe(df.head(10), use_container_width=True)

st.sidebar.header("Filtre")

# Filtru după gen
if "Genre" in df.columns:
    genuri = df["Genre"].dropna().unique().tolist()
    selectie_gen = st.sidebar.multiselect("Alege genurile", genuri, default=genuri)
else:
    selectie_gen = []

# Filtru după preț
if pret_col:
    pret_min, pret_max = float(df[pret_col].min()), float(100)
    selectie_pret = st.sidebar.slider("Selectează intervalul de preț", pret_min, pret_max, (pret_min, pret_max))
else:
    selectie_pret = (None, None)

# Aplicăm filtrele
df_filtrat = df.copy()
if selectie_gen:
    df_filtrat = df_filtrat[df_filtrat["Genre"].isin(selectie_gen)]
if pret_col and selectie_pret != (None, None):
    df_filtrat = df_filtrat[(df_filtrat[pret_col] >= selectie_pret[0]) & (df_filtrat[pret_col] <= selectie_pret[1])]

# ── Rating mediu per gen ─────────────────────────────
if {"Positive_Reviews", "Negative_Reviews", "Genre"}.issubset(df_filtrat.columns):
    df_rating = df_filtrat.groupby("Genre")[["Positive_Reviews", "Negative_Reviews"]].sum()
    df_rating["Rating_Percent"] = df_rating["Positive_Reviews"] / (df_rating["Positive_Reviews"] + df_rating["Negative_Reviews"]) * 100
    df_rating = df_rating.reset_index()

    fig = px.bar(df_rating, x="Genre", y="Rating_Percent", color="Genre",
                 title="Procent de review-uri pozitive pe gen")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nu există suficiente date pentru a calcula rating-ul per gen.")

# ── Distribuția prețurilor ───────────────────────────
if pret_col:
    fig2, ax = plt.subplots(figsize=(9, 4))
    ax.hist(df_filtrat[pret_col].dropna(), bins=20, color="#ff5c00", edgecolor="white")
    ax.set_title("Distribuția prețurilor jocurilor Steam")
    ax.set_xlabel("Preț ($)")
    ax.set_ylabel("Număr de jocuri")
    st.pyplot(fig2)
    plt.close(fig2)
else:
    st.info("Coloana de preț nu este disponibilă în acest CSV.")
