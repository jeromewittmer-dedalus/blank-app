import csv
import html
import io
import math
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).parent / "data"


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    visible_rows = rows[:100]
    column_count = max([len(headers), *(len(row) for row in visible_rows)])
    display_headers = headers + [
        f"Colonne supplémentaire {index}"
        for index in range(1, column_count - len(headers) + 1)
    ]
    header_html = "".join(f"<th>{html.escape(header, quote=True)}</th>" for header in display_headers)
    rows_html = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(row[index], quote=True) if index < len(row) else ''}</td>"
            for index in range(column_count)
        )
        + "</tr>"
        for row in visible_rows
    )
    return f"""
        <style>
            .csv-table-container {{ overflow-x: auto; border: 1px solid #d5deeb; border-radius: 10px; }}
            .csv-dashboard-table {{ width: 100%; border-collapse: collapse; color: #233044; font-size: 0.9rem; }}
            .csv-dashboard-table th {{ background: #1d4ed8; color: #fff; padding: 0.75rem; text-align: left; }}
            .csv-dashboard-table td {{ padding: 0.7rem 0.75rem; border-bottom: 1px solid #e2e8f0; white-space: pre-wrap; overflow-wrap: anywhere; }}
            .csv-dashboard-table tbody tr:nth-child(even) {{ background: #f1f5f9; }}
            .csv-dashboard-table tbody tr:hover {{ background: #dbeafe; }}
        </style>
        <div class="csv-table-container">
            <table class="csv-dashboard-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """


st.set_page_config(layout="wide")
st.markdown(
    "<style>.block-container { max-width: 90vw; padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }</style>",
    unsafe_allow_html=True,
)
st.title("Dashboard de données CSV")
st.write("Recherchez, triez et consultez vos données.")

existing_files = sorted(
    (
        path
        for path in DATA_DIR.glob("*")
        if path.is_file() and path.suffix.lower() == ".csv"
    ),
    key=lambda path: path.name.casefold(),
)

content = None
filename = None
uploaded_file = None

with st.expander("Choisir ou importer un fichier", expanded=not existing_files):
    if existing_files:
        source = st.radio(
            "Source des données",
            ["Utiliser un fichier existant", "Importer un nouveau fichier"],
            horizontal=True,
        )
    else:
        source = "Importer un nouveau fichier"

    if source == "Utiliser un fichier existant":
        selected_file = st.selectbox(
            "Fichier CSV",
            options=existing_files,
            format_func=lambda path: path.name,
        )
        try:
            content = selected_file.read_bytes()
            filename = selected_file.name
        except OSError as error:
            st.error(f"Impossible de lire le fichier : {error}")
    else:
        uploaded_file = st.file_uploader("Importer un nouveau fichier CSV", type=["csv"])
        if uploaded_file is not None:
            filename = Path(uploaded_file.name.replace("\\", "/")).name
            if not filename or Path(filename).suffix.lower() != ".csv":
                st.error("Veuillez sélectionner un fichier avec l’extension `.csv`.")
            else:
                content = uploaded_file.getvalue()
        else:
            st.info("Sélectionnez un fichier CSV pour afficher le dashboard.")

if content is not None:
    try:
        csv_text = content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(csv_text), delimiter=";", strict=True)
        rows = list(reader)
        if not rows or not any(field.strip() for field in rows[0]):
            st.error("Le fichier CSV est vide ou ne contient pas d’en-tête.")
        else:
            headers = rows[0]
            data_rows = rows[1:]
            if uploaded_file is not None:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                destination = DATA_DIR / filename
                destination.write_bytes(content)
                st.success(f"Fichier enregistré dans `{destination.relative_to(Path(__file__).parent)}`.")
            else:
                st.caption(f"Fichier chargé : `{filename}`")
            st.caption(f"Résumé : {len(data_rows)} lignes | {len(headers)} colonnes")

            visible_columns = st.multiselect(
                "Colonnes à afficher",
                options=range(len(headers)),
                default=list(range(len(headers))),
                format_func=lambda index: headers[index] or f"Colonne {index + 1}",
            )
            search = st.text_input("Rechercher dans toutes les colonnes")
            controls = st.columns(2)
            sort_column = controls[0].selectbox(
                "Trier par",
                options=range(len(headers)),
                format_func=lambda index: headers[index] or f"Colonne {index + 1}",
            )
            sort_order = controls[1].selectbox("Ordre", ["Croissant", "Décroissant"])

            matching_rows = [
                row
                for row in data_rows
                if not search or any(search.casefold() in value.casefold() for value in row)
            ]

            def sort_key(row: list[str]) -> tuple[int, float | str]:
                value = row[sort_column].strip() if sort_column < len(row) else ""
                if not value:
                    return (2, "")
                try:
                    number = float(value)
                except ValueError:
                    return (1, value.casefold())
                return (0, number) if math.isfinite(number) else (2, "")

            populated_rows = [
                row for row in matching_rows if sort_key(row)[0] != 2
            ]
            empty_rows = [row for row in matching_rows if sort_key(row)[0] == 2]
            populated_rows.sort(key=sort_key, reverse=sort_order == "Décroissant")
            sorted_rows = populated_rows + empty_rows

            st.caption(f"{len(sorted_rows)} résultat(s) — affichage des 100 premières lignes.")
            if visible_columns:
                visible_headers = [headers[index] for index in visible_columns]
                visible_rows = [
                    [row[index] if index < len(row) else "" for index in visible_columns]
                    for row in sorted_rows
                ]
                st.markdown(render_table(visible_headers, visible_rows), unsafe_allow_html=True)
            else:
                st.info("Sélectionnez au moins une colonne à afficher.")
    except UnicodeDecodeError:
        st.error("Le fichier doit être encodé en UTF-8.")
    except csv.Error as error:
        st.error(f"Le fichier CSV n’a pas pu être lu : {error}")
    except OSError as error:
        st.error(f"Impossible d’enregistrer le fichier : {error}")
