import json
import pathlib
from helpers.db_connector import DatabaseConnector


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def generate_html_from_template(template_path, mapping, data, paper_format="A4"):
    # Lade das HTML-Template
    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()
    # Erstelle ein Dictionary, das den Platzhaltern entsprechende Werte zuweist
    data_dict = {}
    for placeholder, index in mapping.items():
        data_dict[placeholder] = data[index]
    # Papierformat in das Dictionary einfügen
    data_dict['paper_format'] = paper_format
    # Ersetze die Platzhalter im Template
    html_content = template_content.format(**data_dict)
    return html_content


def main():
    # Lade die Konfiguration
    config = load_config("serienbrief_config.json")

    # Erstelle die Datenbankverbindung
    db_config = config["db_config"]
    db = DatabaseConnector(
        db_config["driver"],
        db_config["server"],
        db_config["database"],
        db_config["auth_type"],
        db_config["username"],
        db_config["password"]
    )

    try:
        db.connect()
        print("Datenbankverbindung erfolgreich hergestellt.")
    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        return

    # Gehe alle definierten Serienbriefe durch
    for brief in config["serienbriefe"]:
        query = brief["query"]
        template_path = brief["template"]
        mapping = brief["mapping"]
        paper_format = brief.get("paper_format", "A4")

        try:
            columns, results = db.execute_query(query)
        except Exception as e:
            print(f"Fehler bei Abfrage '{query}': {e}")
            continue

        # Erstelle für jeden Datensatz einen Serienbrief
        for row in results:
            html_content = generate_html_from_template(template_path, mapping, row, paper_format)
            # Definiere den Dateinamen (hier mit dem Serienbrief-Namen und einer ID)
            pathlib.Path("./druck").mkdir(exist_ok=True)
            filename = f"./druck/{brief['name']}_{row[0]}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"Datei {filename} wurde erstellt.")


if __name__ == '__main__':
    main()
