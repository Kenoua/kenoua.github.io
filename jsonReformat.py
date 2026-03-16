import json
import os

def reformat_quest_json_readable(filename):
    if not os.path.exists(filename):
        print(f"Erreur : Le fichier {filename} n'existe pas.")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Erreur : Le fichier JSON est mal formé.")
            return

    formatted_entries = []
    
    for quest in data:
        # On formate chaque item pour qu'il tienne sur une ligne avec son indentation
        req_list = [f'      {json.dumps(r)}' for r in quest.get("requirements", [])]
        res_list = [f'      {json.dumps(r)}' for r in quest.get("results", [])]
        
        # On joint les items avec un retour à la ligne et une virgule
        req_string = ",\n".join(req_list)
        res_string = ",\n".join(res_list)

        # Construction du bloc de la quête
        entry =  '  {\n'
        entry += f'    "name": "{quest.get("name", "")}",\n'
        entry += f'    "category": "{quest.get("category", "")}",\n'
        
        # Requirements
        if req_list:
            entry += f'    "requirements": [\n{req_string}\n    ],\n'
        else:
            entry += '    "requirements": [],\n'
            
        # Results
        if res_list:
            entry += f'    "results": [\n{res_string}\n    ]\n'
        else:
            entry += '    "results": []\n'
            
        entry += '  }'
        formatted_entries.append(entry)

    final_output = "[\n" + ",\n".join(formatted_entries) + "\n]"

    with open("quests_fixed.json", "w", encoding='utf-8') as f:
        f.write(final_output)

    print(f"Succès ! Fichier aéré enregistré sous : quests_fixed.json")

reformat_quest_json_readable('quests.json')
