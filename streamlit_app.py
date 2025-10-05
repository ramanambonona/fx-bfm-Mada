# -*- coding: utf-8 -*-
import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
from requests_toolbelt import MultipartEncoder
import altair as alt
from io import BytesIO

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(
    page_title="Analyse Taux de Change BFM",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === CSS PERSONNALISÉ - STYLE IOS MINIMALISTE ===
st.markdown("""
<style>
/* Masquer éléments Streamlit par défaut ciblés */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
/* On cache UNIQUEMENT le footer natif Streamlit, pas nos footers perso */
div[data-testid="stFooter"] {visibility: hidden;}

/* (Option) masquer le bouton de sidebar si vous le souhaitez.
   Commentez la règle suivante pour l'afficher. */
[data-testid="collapsedControl"] { display: none !important; }

/* Police Garamond partout */
* { font-family: "Garamond","EB Garamond","Times New Roman",serif !important; }

/* Thème général */
.stApp { background-color: #FFFFFF; }

/* Titres */
h1, h2, h3 { color: #2C2C2C; font-weight: 600; letter-spacing: -0.3px; }
h1 { font-size: 2.5rem !important; margin-bottom: 2rem !important; }
h2 { font-size: 1.8rem !important; margin-top: 2rem !important; }
@media (max-width: 768px) {
  h1 { font-size: 1.8rem !important; }
  h2 { font-size: 1.5rem !important; }
  h3 { font-size: 1.3rem !important; }
}

/* Tabs collants et transparents */
.stTabs { position: relative; z-index: 999; }
.stTabs [data-baseweb="tab-list"]{
  position: sticky; top: 0; z-index: 999;
  background: rgba(255,255,255,0.65);
  -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
  border: 1px solid rgba(229,229,229,0.6);
  border-radius: 12px; padding: 6px; gap: 8px; flex-wrap: wrap;
}
@media (max-width: 768px) {
  .stTabs [data-baseweb="tab-list"] { gap: 4px; }
  .stTabs [data-baseweb="tab"] { font-size: 13px; padding: 8px 12px; }
}
.stTabs [data-baseweb="tab"] { color:#8E8E93; font-weight:500; transition: all .3s ease; border-radius:8px; }
.stTabs [aria-selected="true"]{ background: rgba(255,255,255,0.9)!important; color:#2C2C2C!important; }

/* Boutons iOS style */
.stButton>button {
  background-color: transparent !important; color: #2C2C2C !important;
  border: 1.5px solid rgba(44,44,44,0.3) !important; border-radius: 12px;
  padding: 12px 24px; font-weight: 500; font-size: 15px;
  transition: all 0.3s ease; backdrop-filter: blur(5px); width: 100%;
}
@media (max-width: 768px) { .stButton>button { padding: 10px 16px; font-size: 14px; } }
.stButton>button:hover {
  background-color: rgba(44,44,44,0.1) !important; border-color: rgba(44,44,44,0.7) !important;
  transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Download buttons style */
.stDownloadButton>button {
  background-color: rgba(44,44,44,0.9) !important; color: #FFF !important;
  border: 1.5px solid #2C2C2C !important; border-radius: 12px; padding: 12px 24px;
  font-weight: 500; transition: all .3s ease;
}
.stDownloadButton>button:hover { background-color: rgba(44,44,44,0.7) !important; }

/* Inputs */
.stTextInput>div>div>input, .stSelectbox>div>div>select,
.stNumberInput>div>div>input, .stDateInput>div>div>input {
  border:1px solid rgba(229,229,229,0.7); border-radius:10px; padding:10px;
  background-color: rgba(248,248,248,0.8); transition: all .3s ease; font-size:15px;
}
@media (max-width:768px){
  .stTextInput>div>div>input, .stSelectbox>div>div>select,
  .stNumberInput>div>div>input, .stDateInput>div>div>input { font-size:14px; padding:8px; }
}
.stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus,
.stNumberInput>div>div>input:focus, .stDateInput>div>div>input:focus {
  border-color: rgba(44,44,44,0.5); box-shadow: 0 0 0 2px rgba(44,44,44,0.1);
}

/* Metrics */
[data-testid="stMetricValue"] { color:#2C2C2C; font-size:28px; font-weight:600; }
[data-testid="stMetricLabel"] { font-size:14px; color:#8E8E93; }
@media (max-width:768px){
  [data-testid="stMetricValue"]{ font-size:22px; }
  [data-testid="stMetricDelta"]{ font-size:12px; }
}
[data-testid="metric-container"]{
  border:1px solid rgba(229,229,229,0.5); border-radius:12px;
  padding:1rem; background-color: rgba(255,255,255,0.7); backdrop-filter: blur(5px);
}

/* DataFrames */
.stDataFrame{ border-radius:12px; overflow-x:auto; border:1px solid rgba(229,229,229,0.5); }
@media (max-width:768px){ .stDataFrame{ font-size:12px; } }

/* Colonnes responsive */
.row-widget.stHorizontal{ flex-wrap:wrap; }
@media (max-width:768px){
  .row-widget.stHorizontal > div { min-width:100%!important; margin-bottom:10px; }
}

/* Espacement principal */
.main .block-container { padding-top: 2rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
@media (max-width:768px){
  .main .block-container { padding-top:1rem; padding-left:.5rem; padding-right:.5rem; }
}

/* Caption */
.caption { color:#8E8E93; font-size:14px; text-align:center; margin-top:2rem; }

/* Spinner */
.stSpinner > div { border-top-color: rgba(44,44,44,0.8)!important; }

/* Logo flottant (haut-droit) */
a.top-logo {
  position: fixed; top: 8px; right: 12px; z-index: 1001; opacity: .9;
  background: rgba(255,255,255,0.65); border: 1px solid rgba(229,229,229,.6);
  border-radius: 12px; padding: 6px; -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
}
a.top-logo img { height: 24px; width: 24px; display:block; }

/* Footer perso (bas-centre) */
.custom-footer {
  position: fixed;
  left: 50%;
  bottom: 10px;
  transform: translateX(-50%);
  z-index: 1001;

  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(229,229,229,.6);
  border-radius: 12px;
  padding: 8px 12px;

  display: flex;
  align-items: center;
  gap: 12px;

  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
}

.custom-footer .footnote {
  margin: 0;
  color:#2C2C2C;
  font-size: 13px;
  text-align: center;
}

.custom-footer .social {
  display:flex;
  align-items:center;
  gap:8px;
}

.custom-footer .social img {
  height:18px;
  width:18px;
  filter: grayscale(100%);
  opacity:.85;
  transition: opacity .2s;
}

.custom-footer .social img:hover { opacity:1; }

/* Responsive : garde le footer centré et lisible sur mobile */
@media (max-width: 640px) {
  .custom-footer{
    width: calc(100% - 24px);
    padding: 8px 10px;
    bottom: 8px;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
  }
}


</style>
""", unsafe_allow_html=True)

# === LOGO CLIQUABLE (haut-droit) ===
st.markdown(
    '<a class="top-logo" href="https://ramanambonona.github.io" target="_blank" rel="noopener" title="ramanambonona.github.io">'
    '<img src="https://img.icons8.com/?size=100&id=59817&format=png&color=000000" alt="Site web"/></a>',
    unsafe_allow_html=True
)

# === CONSTANTES & HELPERS ===
MOIS_FR = {
    1: 'janv', 2: 'févr', 3: 'mars', 4: 'avr', 5: 'mai', 6: 'juin',
    7: 'juil', 8: 'août', 9: 'sept', 10: 'oct', 11: 'nov', 12: 'déc'
}

def format_date_fr(dt: pd.Timestamp) -> str:
    return f"{dt.day:02d}-{MOIS_FR[dt.month]}-{str(dt.year)[-2:]}"

def label_base_date(dt: pd.Timestamp, mode: str) -> str:
    if mode == "D": return format_date_fr(dt)
    if mode == "M": return f"{MOIS_FR[dt.month]}-{str(dt.year)[-2:]}"
    if mode == "Y": return f"{dt.year}"
    return str(dt)

def fmt_mga(x: float, with_unit: bool = True) -> str:
    s = f"{x:,.2f}".replace(",", " ")
    return f"{s} MGA" if with_unit else s

def ariary_variation_pct(start: float, end: float) -> float:
    if pd.isna(start) or pd.isna(end) or start == 0: return 0.0
    return ((start - end) / start) * 100  # + => Ariary s’apprécie ; - => se déprécie

# === FONCTIONS DONNÉES & CHARTS ===
def fetch_data(date_debut, date_fin, devise):
    url = 'https://www.banky-foibe.mg/admin/wp-json/bfm/cours_mid_en_ar_filter'
    fields = {
        'dateFilterDebut': date_debut.strftime("%Y/%m/%d"),
        'dateFilterFin': date_fin.strftime("%Y/%m/%d"),
        'filterData': devise
    }
    boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": m.content_type,
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.banky-foibe.mg",
        "Referer": "https://www.banky-foibe.mg/marche_marche-de-change"
    }
    try:
        response = requests.post(url, headers=headers, data=m, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Erreur de connexion à l'API : {str(e)}")
        return None

def process_data(json_data, devise):
    try:
        cours_mid = json_data['data']['data']['coursMid']
        df = pd.DataFrame.from_dict(cours_mid, orient='index', columns=[devise])
        df.index = pd.to_datetime(df.index)
        df[devise] = (
            df[devise].astype(str)
            .str.replace(r'\s+', '', regex=True)
            .str.replace(',', '.')
            .astype(float)
        )
        return df.sort_index()
    except Exception as e:
        st.error(f"Erreur de traitement des données : {str(e)}")
        return pd.DataFrame()

def calculate_variation(df, devise):
    if df.empty or devise not in df.columns: return 0.0, 0.0, 0.0
    start = df[devise].iloc[0]; end = df[devise].iloc[-1]
    variation = ((end - start) / start) * 100
    return start, end, variation

def create_altair_chart(data: pd.DataFrame, x_field: str, y_fields: list, chart_type: str = 'line', title: str = ''):
    # Domaine Y
    all_values = []
    for f in y_fields:
        if f in data.columns:
            all_values.extend(pd.to_numeric(data[f], errors='coerce').dropna().tolist())
    y_domain = None
    if len(all_values) > 0:
        y_min, y_max = min(all_values), max(all_values)
        margin = (y_max - y_min) * 0.02 if y_max > y_min else 1.0
        y_domain = [y_min - margin, y_max + margin]

    # Encodage X et libellés (éviter troncature)
    axis_title = 'Date'
    x_enc = x_field
    if x_field == 'index':
        x_enc = 'index:T'
        axis_title = 'Date'
    elif x_field.startswith('Mois'):
        axis_title = 'Mois'
        x_enc = 'Mois:N'
    elif x_field.startswith('Année'):
        axis_title = 'Année'
        x_enc = 'Année:N'

    base = (
        alt.Chart(data)
        .transform_fold(y_fields, as_=['Série', 'Valeur'])
        .encode(
            x=alt.X(
                x_enc,
                axis=alt.Axis(
                    title=axis_title,
                    labelAngle=-45,
                    labelAlign='right',
                    labelBaseline='middle',
                    labelPadding=12,
                    labelLimit=1000,
                    titleFont='Garamond',
                    labelFont='Garamond',
                    titleFontSize=13,
                    labelFontSize=11
                )
            ),
            y=alt.Y(
                'Valeur:Q',
                axis=alt.Axis(
                    title='Taux (MGA)',
                    labelFontSize=11,
                    titleFontSize=13,
                    labelFont='Garamond',
                    titleFont='Garamond',
                    format='.2f'
                ),
                scale=alt.Scale(domain=y_domain) if y_domain else alt.Scale()
            ),
            color=alt.Color(
                'Série:N',
                legend=alt.Legend(title='Série', orient='top', labelFont='Garamond', titleFont='Garamond'),
                scale=alt.Scale(range=['#2C2C2C','#8B4513','#1E90FF','#228B22','#7F7F7F','#8A2BE2','#FF8C00','#2E8B57'])
            ),
            tooltip=[
                alt.Tooltip(x_enc, title=axis_title),
                alt.Tooltip('Série:N', title='Série'),
                alt.Tooltip('Valeur:Q', format='.2f', title='Taux (MGA)')
            ]
        )
    )

    if chart_type == 'line':
        chart = base.mark_line(point=False, strokeWidth=2)
    elif chart_type == 'bar':
        chart = base.mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    elif chart_type == 'area':
        chart = base.mark_area(opacity=0.6, line={'strokeWidth': 2})
    else:
        chart = base.mark_line()

    chart = chart.properties(
        width='container',
        height=450,
        padding={"left": 10, "right": 10, "top": 10, "bottom": 60},  # évite troncatures X
        title=alt.TitleParams(text=title, fontSize=16, font='Garamond', anchor='start', color='#2C2C2C')
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        gridColor='rgba(229,229,229,0.5)',
        domainColor='rgba(229,229,229,0.7)'
    )

    return chart

def create_download_buttons(df, prefix):
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(sep=';', decimal=',', encoding='utf-8-sig', index=False)
        st.download_button("📥 Télécharger CSV", csv, f"{prefix}.csv", "text/csv",
                           use_container_width=True, key=f"dl_csv_{prefix}")
    with col2:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Télécharger Excel", output.getvalue(), f"{prefix}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, key=f"dl_xlsx_{prefix}")

# === INTERFACE UTILISATEUR ===
st.title("📈 Analyse des Taux de Change")
st.caption("Banky Foiben'ny Madagasikara")

tab1, tab2, tab3 = st.tabs(["📅 Journalier", "📆 Mensuel", "📊 Annuel"])
devises_disponibles = ["EUR", "USD", "JPY", "GBP", "CHF", "CNY", "ZAR"]

# === ONGLET JOURNALIER ===
with tab1:
    st.subheader("Analyse Journalière")

    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date de début", datetime.today() - timedelta(days=365), key="j_date_debut")
    with col2:
        date_fin = st.date_input("Date de fin", datetime.today(), key="j_date_fin")

    devises = st.multiselect("Sélectionnez jusqu'à 2 devises", devises_disponibles,
                             default=["EUR","USD"], max_selections=2, key="j_devises")

    if len(devises) >= 1:
        with st.spinner("Chargement des données..."):
            dfs = {}
            for devise in devises:
                data = fetch_data(date_debut, date_fin, devise)
                if data: dfs[devise] = process_data(data, devise)

        if dfs and not any(df.empty for df in dfs.values()):
            full_dates = pd.date_range(date_debut, date_fin)
            combined = pd.concat(dfs.values(), axis=1).reindex(full_dates).ffill().bfill()
            combined['Date_Str'] = combined.index.map(format_date_fr)

            # --- Appréciation/Dépréciation (couleur + base) ---
            st.subheader("Appréciation/Dépréciation")
            base_txt = label_base_date(combined.index[0], "D")
            cols = st.columns(len(devises))
            for i, devise in enumerate(devises):
                start, end, _ = calculate_variation(combined, devise)
                d_ariary = ariary_variation_pct(start, end)
                with cols[i]:
                    st.metric(
                        label=f"Ariary vs {devise} • base {base_txt}",
                        value=f"{fmt_mga(end)}/{devise}",
                        delta=f"{d_ariary:+.2f}%",
                        delta_color="normal"
                    )

            # --- Graphique ---
            st.subheader("Évolution du taux de change")
            chart = create_altair_chart(combined.reset_index(), 'index', devises, 'line',
                                        f"Évolution {' vs '.join(devises)}")
            st.altair_chart(chart, use_container_width=True)

            # --- Export ---
            st.subheader("Télécharger les données")
            download_df = combined[['Date_Str'] + devises].copy()
            download_df.columns = ['Date'] + devises
            create_download_buttons(download_df, f"journalier_{'_'.join(devises)}")
        else:
            st.warning("Aucune donnée disponible pour la période sélectionnée")
    else:
        st.info("Sélectionnez au moins une devise pour commencer l'analyse")

# === ONGLET MENSUEL ===
with tab2:
    st.subheader("Analyse Mensuelle")

    col1, col2 = st.columns(2)
    with col1:
        mois_debut = st.date_input("Mois de début", datetime(2020,1,1), key="m_date_debut").replace(day=1)
    with col2:
        mois_fin = st.date_input("Mois de fin", datetime.today(), key="m_date_fin").replace(day=1)

    devise = st.selectbox("Devise", devises_disponibles, index=0, key="m_devise")

    if st.button("Analyser", key="m_btn"):
        with st.spinner("Analyse en cours..."):
            data = fetch_data(mois_debut, mois_fin, devise)
            if data:
                df = process_data(data, devise)
                if not df.empty:
                    df_mensuel = df.resample('M').mean().ffill()
                    df_mensuel['Mois'] = df_mensuel.index.to_period('M').strftime("%b-%y")

                    start, end, _ = calculate_variation(df_mensuel, devise)
                    d_ariary = ariary_variation_pct(start, end)
                    base_txt = label_base_date(df_mensuel.index[0], "M")

                    st.subheader("Appréciation/Dépréciation mensuelle")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Début", f"{fmt_mga(start)}/{devise}")
                    with cols[1]:
                        st.metric("Fin", f"{fmt_mga(end)}/{devise}")
                    with cols[2]:
                        st.metric(
                            label=f"Ariary vs {devise} • base {base_txt}",
                            value="—",
                            delta=f"{d_ariary:+.2f}%",
                            delta_color="normal"
                        )

                    st.subheader("Évolution mensuelle")
                    chart = create_altair_chart(df_mensuel.reset_index(), 'Mois:N', [devise], 'bar',
                                                f"Taux mensuel moyen - {devise}")
                    st.altair_chart(chart, use_container_width=True)

                    st.subheader("Export des données")
                    create_download_buttons(df_mensuel[['Mois', devise]], f"mensuel_{devise}")
                else:
                    st.warning("Aucune donnée disponible")
            else:
                st.error("Erreur de récupération des données")

# === ONGLET ANNUEL ===
with tab3:
    st.subheader("Analyse Annuelle")

    col1, col2 = st.columns(2)
    with col1:
        annee_debut = st.number_input("Année début", min_value=2000, max_value=2100, value=2020, key="a_annee_debut")
    with col2:
        annee_fin = st.number_input("Année fin", min_value=2000, max_value=2100,
                                    value=datetime.now().year, key="a_annee_fin")

    devise = st.selectbox("Devise", devises_disponibles, index=0, key="a_devise")

    if st.button("Analyser", key="a_btn"):
        with st.spinner("Analyse en cours..."):
            date_debut = datetime(annee_debut, 1, 1)
            date_fin = datetime(annee_fin, 12, 31)
            data = fetch_data(date_debut, date_fin, devise)

            if data:
                df = process_data(data, devise)
                if not df.empty:
                    df_annuel = df.resample('Y').mean().ffill()
                    df_annuel['Année'] = df_annuel.index.year

                    start, end, _ = calculate_variation(df_annuel, devise)
                    d_ariary = ariary_variation_pct(start, end)
                    base_txt = label_base_date(df_annuel.index[0], "Y")

                    st.subheader("Appréciation/Dépréciation annuelle")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Début", f"{fmt_mga(start)}/{devise}")
                    with cols[1]:
                        st.metric("Fin", f"{fmt_mga(end)}/{devise}")
                    with cols[2]:
                        st.metric(
                            label=f"Ariary vs {devise} • base {base_txt}",
                            value="—",
                            delta=f"{d_ariary:+.2f}%",
                            delta_color="normal"
                        )

                    st.subheader("Évolution annuelle")
                    chart = create_altair_chart(df_annuel.reset_index(), 'Année:N', [devise], 'area',
                                                f"Taux annuel moyen - {devise}")
                    st.altair_chart(chart, use_container_width=True)

                    st.subheader("Export des données")
                    create_download_buttons(df_annuel[['Année', devise]], f"annuel_{devise}")
                else:
                    st.warning("Aucune donnée disponible")
            else:
                st.error("Erreur de récupération des données")

# === FOOTER PERSONNALISÉ ===
st.markdown("""
<div class="custom-footer">
  <p class="footnote">Ramanambonona Ambinintsoa, Ph.D</p>
  <div class="social">
    <a href="mailto:ambinintsoa.uat.ead2@gmail.com" aria-label="Mail">
      <img src="https://img.icons8.com/?size=100&id=86875&format=png&color=000000" alt="Mail">
    </a>
    <a href="https://github.com/ramanambonona" target="_blank" rel="noopener" aria-label="GitHub">
      <img src="https://img.icons8.com/?size=100&id=3tC9EQumUAuq&format=png&color=000000" alt="GitHub">
    </a>
    <a href="https://www.linkedin.com/in/ambinintsoa-ramanambonona" target="_blank" rel="noopener" aria-label="LinkedIn">
      <img src="https://img.icons8.com/?size=100&id=8808&format=png&color=000000" alt="LinkedIn">
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

# Bande séparatrice + note
st.markdown("---")
st.markdown(
    '<p class="caption">Données fournies par la Banque Foiben\'ny Madagasikara • Mise à jour quotidienne</p>',
    unsafe_allow_html=True
)
