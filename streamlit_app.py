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

# Configuration des constantes
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

    response = requests.post(url, headers=headers, data=m)
    return response.json() if response.status_code == 200 else None

def process_data(json_data, devise):
    """Traite les données brutes avec conversion décimale correcte"""
    try:
        cours_mid = json_data['data']['data']['coursMid']
        df = pd.DataFrame.from_dict(cours_mid, orient='index', columns=[devise])
        df.index = pd.to_datetime(df.index)
        
        # Conversion numérique corrigée
        df[devise] = (
            df[devise].astype(str)
            .str.replace('\s+', '', regex=True)  # Supprime les espaces
            .str.replace(',', '.')            # Remplace virgule par point
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

def create_download_buttons(df, prefix):
    """Crée les boutons de téléchargement CSV/Excel"""
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(sep=';', decimal=',', encoding='utf-8-sig')
        st.download_button(
            "📥 Télécharger CSV",
            csv,
            f"{prefix}.csv",
            "text/csv"
        )
    
    with col2:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer)
        st.download_button(
            "📥 Télécharger Excel",
            data=output.getvalue(),
            file_name=f"{prefix}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# Interface utilisateur
st.set_page_config(page_title="Analyse Taux de Change BFM", layout="wide")
st.title("📈 Analyse des Taux de Change - Banky Foiben'ny Madagasikara")
tab1, tab2, tab3 = st.tabs(["Journalier", "Mensuel", "Annuel"])

devises_disponibles = ["EUR", "USD", "JPY", "GBP", "CHF", "CNY", "ZAR"]

# Onglet Journalier
with tab1:
    st.subheader("Analyse Journalière")
    col1, col2 = st.columns(2)
    
    with col1:
        date_debut = st.date_input("Date de début", datetime.today() - timedelta(days=1800), key="j_date_debut")
    with col2:
        date_fin = st.date_input("Date de fin", datetime.today(), key="j_date_fin")
    
    devises = st.multiselect(
        "Sélectionnez 2 devises", 
        devises_disponibles, 
        default=["EUR", "USD"], 
        max_selections=2,
        key="j_devises"
    )
    
    if len(devises) == 2:
        dfs = {}
        for devise in devises:
            data = fetch_data(date_debut, date_fin, devise)
            dfs[devise] = process_data(data, devise)
        
        if not any(df.empty for df in dfs.values()):
            full_dates = pd.date_range(date_debut, date_fin)
            combined = pd.concat(dfs.values(), axis=1).reindex(full_dates).ffill().bfill()
            combined['Date_Str'] = combined.index.map(format_date_fr)
            
            # Vérification des données
            st.write("Aperçu des données brutes :")
            st.dataframe(combined.style.format("{:,.2f}", subset=devises))
            
            # Graphique en ligne
            st.subheader("Évolution du taux de change")
            line_chart = alt.Chart(combined.reset_index()).mark_line().encode(
                x=alt.X('index', axis=alt.Axis(title='Date')),
                y=alt.Y(devises[0], axis=alt.Axis(title='Taux de change')),
                tooltip=['Date_Str', devises[0]]
            ).properties(
                width='container'
            )

            if len(devises) > 1:
                line_chart += alt.Chart(combined.reset_index()).mark_line(color='red').encode(
                    x=alt.X('index', axis=alt.Axis(title='Date')),
                    y=alt.Y(devises[1], axis=alt.Axis(title='Taux de change')),
                    tooltip=['Date_Str', devises[1]]
                )
            st.altair_chart(line_chart, use_container_width=True)
            
            # Indicateurs de variation
            st.subheader("Variation sur la période")
            cols = st.columns(2)
            for i, devise in enumerate(devises):
                start, end, variation = calculate_variation(combined, devise)
                with cols[i]:
                    st.metric(
                        label=f"Performance {devise}",
                        value=f"{end:,.2f} MGA".replace(',', ' '),
                        delta=f"{variation:.2f}%",
                        delta_color="inverse" if variation > 0 else "normal"
                    )
# Dans la section "Onglet Journalier", après les indicateurs de variation :

            # Ajouter cette section de téléchargement
            st.subheader("Télécharger les données journalières")
            download_df = combined[['Date_Str'] + devises].copy()
            download_df.columns = ['Date'] + devises
            create_download_buttons(download_df, f"journalier_{'_'.join(devises)}")

# Onglet Mensuel
with tab2:
    st.subheader("Analyse Mensuelle")
    col1, col2 = st.columns(2)
    
    with col1:
        mois_debut = st.date_input(
            "Mois de début", 
            datetime(2020, 1, 1), 
            format="MM/DD/YYYY",
            key="m_date_debut"
        ).replace(day=1)
    
    with col2:
        mois_fin = st.date_input(
            "Mois de fin", 
            datetime.today(), 
            format="MM/DD/YYYY",
            key="m_date_fin"
        ).replace(day=1)
    
    devise = st.selectbox(
        "Devise", 
        devises_disponibles, 
        index=0,
        key="m_devise"
    )
    
    if st.button("Analyser", key="m_btn"):
        data = fetch_data(mois_debut, mois_fin, devise)
        df = process_data(data, devise)
        
        if not df.empty:
            # Agrégation mensuelle
            df_mensuel = df.resample('M').mean().ffill()
            df_mensuel['Mois'] = df_mensuel.index.to_period('M').strftime("%b-%y")
            
            # Variation
            start, end, variation = calculate_variation(df_mensuel, devise)
            
            st.subheader("Performance mensuelle")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Début", f"{start:.2f} MGA")
            with cols[1]:
                st.metric("Fin", f"{end:.2f} MGA")
            with cols[2]:
                st.metric("Variation", f"{variation:.2f}%", 
                         delta_color="inverse" if variation > 0 else "normal")
            
            # Visualisation
            st.subheader("Évolution mensuelle")
            bars = alt.Chart(df_mensuel.reset_index()).mark_bar().encode(
                x=alt.X('Mois:N', title='Mois', sort=None, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y(f'{devise}:Q', title='Taux moyen (MGA)'),
                tooltip=['Mois:N', alt.Tooltip(f'{devise}:Q', format='.2f')]
            )
            st.altair_chart(bars, use_container_width=True)
            
            # Export
            st.subheader("Export des données")
            create_download_buttons(df_mensuel, f"mensuel_{devise}")

# Onglet Annuel
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
        date_debut = datetime(annee_debut, 1, 1)
        date_fin = datetime(annee_fin, 12, 31)
        data = fetch_data(date_debut, date_fin, devise)
        df = process_data(data, devise)
        
        if not df.empty:
            # Agrégation annuelle
            df_annuel = df.resample('Y').mean().ffill()
            df_annuel['Année'] = df_annuel.index.year
            
            # Variation
            start, end, variation = calculate_variation(df_annuel, devise)
            
            st.subheader("Performance annuelle")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Début", f"{start:.2f} MGA")
            with cols[1]:
                st.metric("Fin", f"{end:.2f} MGA")
            with cols[2]:
                st.metric("Variation", f"{variation:.2f}%", 
                        delta_color="inverse" if variation > 0 else "normal")
            
            # Visualisation
            st.subheader("Évolution annuelle")
            area = alt.Chart(df_annuel.reset_index()).mark_area().encode(
                x=alt.X('Année:N', title='Année'),
                y=alt.Y(f'{devise}:Q', title='Taux moyen (MGA)'),
                tooltip=['Année:N', alt.Tooltip(f'{devise}:Q', format='.2f')]
            )
            st.altair_chart(area, use_container_width=True)
            
            # Export
            st.subheader("Export des données")
            create_download_buttons(df_annuel, f"annuel_{devise}")

st.markdown("---")
st.caption("Données fournies par la Banque Foiben'ny Madagasikara - Mise à jour quotidienne")
