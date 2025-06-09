# Application d'Analyse des Taux de Change - Banky Foiben'ny Madagasikara
Cette application Streamlit permet d'analyser les taux de change quotidiens publiés par la [Banky Foiben'ny Madagascar](https://www.banky-foibe.mg/marche_marche-de-change). 
Elle offre des visualisations interactives et des fonctionnalités d'export de données pour différentes périodes (journalière, mensuelle, annuelle).

## Fonctionnalités Principales

### 📊 Onglet Journalier

- Analyse comparative entre 2 devises sur une période personnalisée

- Graphique linéaire montrant l'évolution des taux

- Indicateurs de performance avec variation en pourcentage

- Export des données au format CSV ou Excel

### 📈 Onglet Annuel

- Analyse des moyennes annuelles pour une devise

- Visualisation sous forme de graphique en aires

- Calcul de la variation inter-annuelle

### 📈 Onglet Annuel

- Analyse des moyennes annuelles pour une devise

- Visualisation sous forme de graphique en aires

- Calcul de la variation inter-annuelle

## Devises Disponibles

- Euro (EUR)

- Dollar Américain (USD)

- Yen Japonais (JPY)

- Livre Sterling (GBP)

- Franc Suisse (CHF)

- Yuan Chinois (CNY)

- Rand Sud-Africain (ZAR)

## Comment Utiliser l'Application

1. Sélectionnez l'onglet correspondant à l'analyse souhaitée (Journalier/Mensuel/Annuel)

2. Choisissez les dates ou périodes d'analyse

3. Sélectionnez les devises à comparer (pour l'analyse journalière)

3. Cliquez sur "Analyser"

4. Visualisez les résultats graphiques et les indicateurs de performance

5. Exportez les données via les boutons CSV/Excel



## Exigences Techniques

### Dépendances

```bash
streamlit
pandas
numpy
requests
altair
requests-toolbelt
```

### Installation
```bash
pip install -r requirements.txt
```

### Exécution

```bash
streamlit run streamlit_app.py

### Source des Données

Les données sont récupérées en temps réel depuis l'API officielle de la **Banky Foiben'ny Madagasikara (Banque Centrale de Madagascar)** :

🌐 [www.banky-foibe.mg](https://www.banky-foibe.mg/marche_marche-de-change)
### Avertissement
> Les données présentées sont mises à jour quotidiennement par la BFM.
> Cette application est un outil d'analyse et ne constitue pas un conseil financier.

---
**Développeur**: *Dr. Ramanambonona Ambinintsoa*
**Dernière mise à jour**: 09 juin 2025
**Données** issues du siteweb de la Banque Centrale de Madagascar
