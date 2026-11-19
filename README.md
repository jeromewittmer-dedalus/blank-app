# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```

### Charger un fichier CSV

Dans l’application, sélectionnez un fichier `.csv` encodé en UTF-8 et séparé par des points-virgules (`;`), ou choisissez-en un déjà présent dans le dossier `data/`. Le choix du fichier et l’import sont repliés par défaut quand un CSV existe déjà. Le dashboard occupe 90 % de la largeur de l’écran ; il permet de rechercher dans toutes les colonnes sans tenir compte de la casse, de choisir les colonnes à afficher et de trier par colonne dans les deux sens. Les 100 premières lignes correspondantes s’affichent dans un tableau coloré. Un fichier importé portant le même nom remplace l’ancien.
