# 💱 Analyse des Taux de Change – *Banky Foiben'ny Madagasikara*

<div align="center">

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**Application pour analyser les taux de change BFM et visualiser l’appréciation/dépréciation de l’Ariary (MGA)**

</div>

---

## 🎯 Vue d’ensemble

Cette application Streamlit permet d’explorer les cours **MGA par devise**  publiés par la *[Banky Foiben'ny Madagascar](https://www.banky-foibe.mg/marche_marche-de-change)* au format **journalier, mensuel et annuel**, avec un indicateur dédié à l’**Ariary** :
- **![Ariary](https://img.shields.io/badge/-%2B2.3%25-brightgreen)** : **Ariary s’apprécie** (il faut **moins** de MGA pour 1 unité de devise)
-  **![Ariary](https://img.shields.io/badge/--2.3%25-ff3b30)** : **Ariary se déprécie** (il faut **plus** de MGA pour 1 unité de devise)
- La **date de base** (début de période) est **toujours affichée** à côté du libellé.
Elle offre des visualisations interactives et des fonctionnalités d'export de données pour différentes périodes (journalière, mensuelle, annuelle).
**![Ariary](https://img.shields.io/badge/-%2B2.3%25-9e9e9e?style=plastic&labelColor=4a4a4a)**
---

## ⚡ Fonctionnalités clés

- **Ariary** : code couleur automatique (vert/rouge) sur l’indicateur d’appréciation/dépréciation
- **Formats multiples** : Journalier (lignes), Mensuel (barres), Annuel (aire)
- **Montants formatés** : `4 000.00 MGA` dans toutes les métriques
- **Exports** : CSV (séparateur `;`, décimale `,`) et Excel (`.xlsx`)

---

## 🧮 Règle de calcul & couleurs

**Définition** (les cours renvoyés par BFM sont **MGA par 1 unité de devise**):  
> Si le taux **baisse** sur la période ⇒ l’**Ariary s’apprécie** ⇒ **+% ![vert](https://img.shields.io/badge/Ariary_%2B2.3%25-vert-brightgreen)**  
> Si le taux **monte** sur la période ⇒ l’**Ariary se déprécie** ⇒ **-% ![rouge](https://img.shields.io/badge/Ariary_%2B2.3%25-deep%20pink?color=ff1493)**

Formule utilisée pour la variation de l’Ariary (inverse du taux):
```python
d_ariary = ((start - end) / start) * 100  # + => appréciation ; - => dépréciation
```

Affichage via `st.metric` (Streamlit colore automatiquement le delta si `delta_color="normal"`):
```python
st.metric(
    label=f"Ariary vs {devise} • base {base_txt}",
    value=f"{end:,.2f} MGA/{devise}".replace(',', ' '),
    delta=f"{d_ariary:+.2f}%",
    delta_color="normal"  # + = vert ; - = rouge
)
```

**Résumé visuel :**  
- Vert ![+2.3%](https://img.shields.io/badge/Ariary_%2B2.3%25-vert-brightgreen) → Ariary **s’apprécie**  
- Rouge ![-2.3%](https://img.shields.io/badge/Ariary_%2B2.3%25-deep%20pink?color=ff1493) → Ariary **se déprécie**

> La **date de base** (`base_txt`) correspond au **premier point** 
de la fenêtre affichée : `JJ-mmm-AA` (journalier), `mmm-AA` (mensuel), `AAAA` (annuel).

---

## 🚀 Démarrage rapide

### En ligne
1. Ouvrez l’application déployée (Streamlit Community Cloud).
2. Choisissez période et devise(s).
3. Lisez les métriques (couleurs) et exportez les données.

### En local
```bash
git clone https://github.com/votre-repo/fx-bfm-mada.git
cd fx-bfm-mada
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

**Prérequis** : Python 3.9+, connexion Internet.

---

## 🧾 Export des données

- **CSV** : séparateur `;`, décimale `,`, encodage `UTF-8-SIG`
- **Excel** : `.xlsx` (feuille unique)
- Colonnes exportées :
  - Journalier : `Date`, `{DEV1}`, `{DEV2}`
  - Mensuel : `Mois`, `{DEV}`
  - Annuel : `Année`, `{DEV}`

---


## ❓ FAQ rapide

- **Pourquoi +% = vert et -% = rouge ?**  
  Parce que la variation porte sur l’**Ariary** (inverse du taux MGA/devise). Une **baisse** du taux signifie qu’il faut **moins** de MGA pour 1 devise → l’Ariary **s’apprécie** → **+% vert**.

- **Mes dates sont tronquées dans les graphiques ?**  
  Nous ajoutons un padding bas et inclinons les labels pour les rendre lisibles.

- **Erreur `StreamlitDuplicateElementId` ?**  
  Les boutons de téléchargement ont des **keys uniques** et sont **hors** des boucles.

---

## 📜 Licence

Projet sous **MIT**. Voir [LICENSE](LICENSE).

---

## 🙏 Remerciements

- **Banky Foiben’ny Madagasikara (BFM)** pour la donnée publique
- **Streamlit**, **Pandas**, **Altair** pour l’écosystème

---



---
**Développeur**: *Dr. Ramanambonona Ambinintsoa*
**Dernière mise à jour**: 09 juin 2025
**Données** issues du siteweb de la Banque Centrale de Madagascar
