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
/* Masquer éléments Streamlit par défaut */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="collapsedControl"] {
    display: none !important;
}

/* Police Garamond pour tout */
* {
    font-family: "Garamond", "EB Garamond", "Times New Roman", serif !important;
}

/* Thème général */
.stApp {
    background-color: #FFFFFF;
}

/* Titres */
h1, h2, h3 {
    color: #2C2C2C;
    font-weight: 600;
    letter-spacing: -0.3px;
}

h1 {
    font-size: 2.5rem !important;
    margin-bottom: 2rem !important;
}

h2 {
    font-size: 1.8rem !important;
    margin-top: 2rem !important;
}

@media (max-width: 768px) {
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.3rem !important; }
}

/* Boutons iOS style */
.stButton>button {
    background-color: transparent !important;
    color: #2C2C2C !important;
    border: 1.5px solid rgba(44, 44, 44, 0.3) !important;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 500;
    font-size: 15px;
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
    width: 100%;
}

@media (max-width: 768px) {
    .stButton>button {
        padding: 10px 16px;
        font-size: 14px;
    }
}

.stButton>button:hover {
    background-color: rgba(44, 44, 44, 0.1) !important;
    border-color: rgba(44, 44, 44, 0.7) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Download buttons style */
.stDownloadButton>button {
    background-color: rgba(44, 44, 44, 0.9) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #2C2C2C !important;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stDownloadButton>button:hover {
    background-color: rgba(44, 44, 44, 0.7) !important;
}

/* Inputs responsive */
.stTextInput>div>div>input,
.stSelectbox>div>div>select,
.stNumberInput>div>div>input,
.stDateInput>div>div>input {
    border: 1px solid rgba(229, 229, 229, 0.7);
    border-radius: 10px;
    padding: 10px;
    background-color: rgba(248, 248, 248, 0.8);
    transition: all 0.3s ease;
    font-size: 15px;
}

@media (max-width: 768px) {
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input,
    .stDateInput>div>div>input {
        font-size: 14px;
        padding: 8px;
    }
}

.stTextInput>div>div>input:focus,
.stSelectbox>div>div>select:focus,
.stNumberInput>div>div>input:focus,
.stDateInput>div>div>input:focus {
    border-color: rgba(44, 44, 44, 0.5);
    box-shadow: 0 0 0 2px rgba(44, 44, 44, 0.1);
}

/* Multiselect */
.stMultiSelect [data-baseweb="tag"] {
    background-color: rgba(44, 44, 44, 0.9);
    border-radius: 8px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(248, 248, 248, 0.8);
    border-radius: 12px;
    padding: 4px;
    backdrop-filter: blur(5px);
    flex-wrap: wrap;
}

@media (max-width: 768px) {
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 13px;
        padding: 8px 12px;
    }
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #8E8E93;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    color: #2C2C2C !important;
}

/* Metrics responsive */
[data-testid="stMetricValue"] {
    color: #2C2C2C;
    font-size: 28px;
    font-weight: 600;
}

[data-testid="stMetricLabel"] {
    font-size: 14px;
    color: #8E8E93;
}

@media (max-width: 768px) {
    [data-testid="stMetricValue"] {
        font-size: 22px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 12px;
    }
}

/* Metric containers */
[data-testid="metric-container"] {
    border: 1px solid rgba(229, 229, 229, 0.5);
    border-radius: 12px;
    padding: 1rem;
    background-color: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(5px);
}

@media (max-width: 768px) {
    [data-testid="metric-container"] {
        padding: 0.75rem;
    }
}

/* DataFrames responsive */
.stDataFrame {
    border-radius: 12px;
    overflow-x: auto;
    border: 1px solid rgba(229, 229, 229, 0.5);
}

@media (max-width: 768px) {
    .stDataFrame {
        font-size: 12px;
    }
}

/* Colonnes responsive */
.row-widget.stHorizontal {
    flex-wrap: wrap;
}

@media (max-width: 768px) {
    .row-widget.stHorizontal > div {
        min-width: 100% !important;
        margin-bottom: 10px;
    }
}

/* Espacement du contenu principal */
.main .block-container {
    padding-top: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 100%;
}

@media (max-width: 768px) {
    .main .block-container {
        padding-top: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
}

/* Alerts responsive */
.stAlert {
    border-radius: 12px;
    border: none;
    backdrop-filter: blur(5px);
}

@media (max-width: 768px) {
    .stAlert {
        font-size: 13px;
        padding: 10px;
    }
}

/* Caption style */
.caption {
    color: #8E8E93;
    font-size: 14px;
    text-align: center;
    margin-top: 2rem;
}

/* Spinner */
.stSpinner > div {
    border-top-color: rgba(44, 44, 44, 0.8) !important;
}
</style>
""", unsafe_allow_html=True)

# === CONSTANTES ===
MOIS_FR = {
    1: 'janv', 2: 'févr', 3: 'mars', 4: 'avr', 5: 'mai', 6: 'juin',
    7: 'juil', 8: 'août', 9: 'sept', 10: 'oct', 11: 'nov', 12: 'déc'
}

def format_date_fr(dt):
    """Formate les dates en français : 01-avr-24"""
    return f"{dt.day:02d}-{MOIS_FR[dt.month]}-{str(dt.year)[-2:]}"

def fetch_data(date_debut, date_fin, devise):
    """Récupère les données depuis l'API BFM"""
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
    """Traite les données brutes avec conversion décimale correcte"""
    try:
        cours_mid = json_data['data']['data']['coursMid']
        df = pd.DataFrame.from_dict(cours_mid, orient='index', columns=[devise])
        df.index = pd.to_datetime(df.index)
        
        df[devise] = (
            df[devise].astype(str)
            .str.replace('\s+', '', regex=True)
            .str.replace(',', '.')
            .astype(float)
        )
        return df.sort_index()
    except Exception as e:
        st.error(f"Erreur de traitement des données : {str(e)}")
        return pd.DataFrame()

def calculate_variation(df, devise):
    """Calcule la variation entre première et dernière valeur"""
    if df.empty or devise not in df.columns:
        return 0.0, 0.0, 0.0
    start = df[devise].iloc[0]
    end = df[devise].iloc[-1]
    variation = ((end - start) / start) * 100
    return start, end, variation

def create_altair_chart(data, x_field, y_fields, chart_type='line', title=''):
    """Crée un graphique Altair stylisé avec axes optimisés"""
    # Calcul des limites y
    all_values = []
    for field in y_fields:
        if field in data.columns:
            all_values.extend(data[field].dropna().tolist())
    
    if all_values:
        y_min = min(all_values)
        y_max = max(all_values)
        # Ajouter une marge de 2%
        margin = (y_max - y_min) * 0.02
        y_domain = [y_min - margin, y_max + margin]
    else:
        y_domain = None
    
    base = alt.Chart(data).encode(
        x=alt.X(x_field, axis=alt.Axis(
            title='Date',
            labelAngle=-45,
            labelFontSize=11,
            titleFontSize=13,
            labelFont='Garamond',
            titleFont='Garamond'
        )),
        tooltip=[alt.Tooltip(x_field, title='Date')] + 
                [alt.Tooltip(f, format='.2f', title=f) for f in y_fields if f in data.columns]
    )
    
    if chart_type == 'line':
        colors = ['#2C2C2C', '#8B4513', '#1E90FF', '#228B22']
        charts = []
        for i, field in enumerate(y_fields):
            if field in data.columns:
                chart = base.mark_line(
                    point=False,
                    strokeWidth=2,
                    color=colors[i % len(colors)]
                ).encode(
                    y=alt.Y(field, 
                           axis=alt.Axis(
                               title='Taux (MGA)',
                               labelFontSize=11,
                               titleFontSize=13,
                               labelFont='Garamond',
                               titleFont='Garamond',
                               format='.2f'
                           ),
                           scale=alt.Scale(domain=y_domain) if y_domain else alt.Scale())
                )
                charts.append(chart)
        final_chart = charts[0]
        for chart in charts[1:]:
            final_chart += chart
            
    elif chart_type == 'bar':
        final_chart = base.mark_bar(
            color='rgba(44, 44, 44, 0.8)',
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8
        ).encode(
            y=alt.Y(y_fields[0], 
                   axis=alt.Axis(
                       title='Taux moyen (MGA)',
                       labelFontSize=11,
                       titleFontSize=13,
                       labelFont='Garamond',
                       titleFont='Garamond',
                       format='.2f'
                   ),
                   scale=alt.Scale(domain=y_domain) if y_domain else alt.Scale())
        )
        
    elif chart_type == 'area':
        final_chart = base.mark_area(
            color='rgba(44, 44, 44, 0.6)',
            line={'color': '#2C2C2C', 'strokeWidth': 2}
        ).encode(
            y=alt.Y(y_fields[0], 
                   axis=alt.Axis(
                       title='Taux moyen (MGA)',
                       labelFontSize=11,
                       titleFontSize=13,
                       labelFont='Garamond',
                       titleFont='Garamond',
                       format='.2f'
                   ),
                   scale=alt.Scale(domain=y_domain) if y_domain else alt.Scale())
        )
    
    final_chart = final_chart.properties(
        width='container',
        height=450,
        title=alt.TitleParams(
            text=title,
            fontSize=16,
            font='Garamond',
            anchor='start',
            color='#2C2C2C'
        )
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        gridColor='rgba(229, 229, 229, 0.5)',
        domainColor='rgba(229, 229, 229, 0.7)'
    )
    
    return final_chart

def create_download_buttons(df, prefix):
    """Crée les boutons de téléchargement CSV/Excel"""
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(sep=';', decimal=',', encoding='utf-8-sig')
        st.download_button(
            "📥 Télécharger CSV",
            csv,
            f"{prefix}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer)
        st.download_button(
            "📥 Télécharger Excel",
            data=output.getvalue(),
            file_name=f"{prefix}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True
        )

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
        date_debut = st.date_input(
            "Date de début", 
            datetime.today() - timedelta(days=365),
            key="j_date_debut"
        )
    with col2:
        date_fin = st.date_input(
            "Date de fin", 
            datetime.today(), 
            key="j_date_fin"
        )
    
    devises = st.multiselect(
        "Sélectionnez jusqu'à 2 devises", 
        devises_disponibles, 
        default=["EUR", "USD"], 
        max_selections=2,
        key="j_devises"
    )
    
    if len(devises) >= 1:
        with st.spinner("Chargement des données..."):
            dfs = {}
            for devise in devises:
                data = fetch_data(date_debut, date_fin, devise)
                if data:
                    dfs[devise] = process_data(data, devise)
        
        if dfs and not any(df.empty for df in dfs.values()):
            full_dates = pd.date_range(date_debut, date_fin)
            combined = pd.concat(dfs.values(), axis=1).reindex(full_dates).ffill().bfill()
            combined['Date_Str'] = combined.index.map(format_date_fr)
            
            # Variation sur la période
            st.subheader("Performance sur la période")
            cols = st.columns(len(devises))
            for i, devise in enumerate(devises):
                start, end, variation = calculate_variation(combined, devise)
                with cols[i]:
                    st.metric(
                        label=f"{devise}",
                        value=f"{end:,.2f} MGA".replace(',', ' '),
                        delta=f"{variation:+.2f}%"
                    )
            
            # Graphique
            st.subheader("Évolution du taux de change")
            chart = create_altair_chart(
                combined.reset_index(),
                'index',
                devises,
                'line',
                f"Évolution {' vs '.join(devises)}"
            )
            st.altair_chart(chart, use_container_width=True)
            
            # Export
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
        mois_debut = st.date_input(
            "Mois de début", 
            datetime(2020, 1, 1),
            key="m_date_debut"
        ).replace(day=1)
    
    with col2:
        mois_fin = st.date_input(
            "Mois de fin", 
            datetime.today(),
            key="m_date_fin"
        ).replace(day=1)
    
    devise = st.selectbox(
        "Devise", 
        devises_disponibles, 
        index=0,
        key="m_devise"
    )
    
    if st.button("Analyser", key="m_btn"):
        with st.spinner("Analyse en cours..."):
            data = fetch_data(mois_debut, mois_fin, devise)
            if data:
                df = process_data(data, devise)
                
                if not df.empty:
                    df_mensuel = df.resample('M').mean().ffill()
                    df_mensuel['Mois'] = df_mensuel.index.to_period('M').strftime("%b-%y")
                    
                    start, end, variation = calculate_variation(df_mensuel, devise)
                    
                    st.subheader("Performance mensuelle")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Début", f"{start:.2f} MGA")
                    with cols[1]:
                        st.metric("Fin", f"{end:.2f} MGA")
                    with cols[2]:
                        st.metric("Variation", f"{variation:+.2f}%")
                    
                    st.subheader("Évolution mensuelle")
                    chart = create_altair_chart(
                        df_mensuel.reset_index(),
                        'Mois:N',
                        [devise],
                        'bar',
                        f"Taux mensuel moyen - {devise}"
                    )
                    st.altair_chart(chart, use_container_width=True)
                    
                    st.subheader("Export des données")
                    create_download_buttons(df_mensuel, f"mensuel_{devise}")
                else:
                    st.warning("Aucune donnée disponible")
            else:
                st.error("Erreur de récupération des données")

# === ONGLET ANNUEL ===
with tab3:
    st.subheader("Analyse Annuelle")
    
    col1, col2 = st.columns(2)
    with col1:
        annee_debut = st.number_input(
            "Année début", 
            min_value=2000, 
            max_value=2100, 
            value=2020,
            key="a_annee_debut"
        )
    
    with col2:
        annee_fin = st.number_input(
            "Année fin", 
            min_value=2000, 
            max_value=2100, 
            value=datetime.now().year,
            key="a_annee_fin"
        )
    
    devise = st.selectbox(
        "Devise", 
        devises_disponibles, 
        index=0,
        key="a_devise"
    )
    
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
                    
                    start, end, variation = calculate_variation(df_annuel, devise)
                    
                    st.subheader("Performance annuelle")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Début", f"{start:.2f} MGA")
                    with cols[1]:
                        st.metric("Fin", f"{end:.2f} MGA")
                    with cols[2]:
                        st.metric("Variation", f"{variation:+.2f}%")
                    
                    st.subheader("Évolution annuelle")
                    chart = create_altair_chart(
                        df_annuel.reset_index(),
                        'Année:N',
                        [devise],
                        'area',
                        f"Taux annuel moyen - {devise}"
                    )
                    st.altair_chart(chart, use_container_width=True)
                    
                    st.subheader("Export des données")
                    create_download_buttons(df_annuel, f"annuel_{devise}")
                else:
                    st.warning("Aucune donnée disponible")
            else:
                st.error("Erreur de récupération des données")

# === FOOTER ===
st.markdown("---")
st.markdown(
    '<p class="caption">Données fournies par la Banque Foiben\'ny Madagasikara • Mise à jour quotidienne</p>',
    unsafe_allow_html=True
)
