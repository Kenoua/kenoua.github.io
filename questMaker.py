import tkinter as tk
from tkinter import messagebox, ttk
import re
import json
import os

class QuestLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quest JSON Exporter")
        
        # --- Config & Data ---
        self.CATEGORIES = ["Quest", "Crafting", "SQI","SQI Bonus", "Betty", "Summer race","Enchantment","Cooking"] # Defined Category Struct
        self.item_requirements = []
        self.item_results = []
        self.item_map = self.load_item_db("cleaned_questItemsDB.txt")
        self.item_names = list(self.item_map.keys())

        # --- Top Section: Quest Info ---
        tk.Label(root, text="Quest Name:").grid(row=0, column=0, sticky="e", pady=2)
        self.quest_entry = tk.Entry(root, width=30)
        self.quest_entry.grid(row=0, column=1, pady=2, padx=5)

        tk.Label(root, text="Category:").grid(row=1, column=0, sticky="e", pady=2)
        self.cat_combo = ttk.Combobox(root, values=self.CATEGORIES, state="readonly", width=27)
        self.cat_combo.set(self.CATEGORIES[0])
        self.cat_combo.grid(row=1, column=1, pady=2, padx=5)

        # --- Middle Section: Item Search ---
        tk.Label(root, text="Search Item:").grid(row=2, column=0, sticky="e", pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_suggestions)
        self.search_entry = tk.Entry(root, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=2, column=1, pady=5)

        self.suggestion_list = tk.Listbox(root, height=4, width=45)
        self.suggestion_list.grid(row=3, column=0, columnspan=2, padx=10)
        self.suggestion_list.bind("<<ListboxSelect>>", self.on_select_suggestion)

        self.selected_id_label = tk.Label(root, text="Selected: None", fg="blue")
        self.selected_id_label.grid(row=4, column=0, columnspan=2)

        tk.Label(root, text="Qty:").grid(row=5, column=0, sticky="e")
        self.qty_entry = tk.Entry(root, width=10)
        self.qty_entry.grid(row=5, column=1, sticky="w", padx=5)

        # --- Buttons: Add to Requirements or Results ---
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="+ Requirement", command=lambda: self.add_item("req"), bg="#fff3cd").pack(side="left", padx=5)
        tk.Button(btn_frame, text="+ Reward (Result)", command=lambda: self.add_item("res"), bg="#d4edda").pack(side="left", padx=5)

        # --- Display Lists ---
        tk.Label(root, text="Current Setup:").grid(row=7, column=0, columnspan=2)
        self.display_box = tk.Listbox(root, height=8, width=50)
        self.display_box.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        tk.Button(root, text="SAVE TO JSON", command=self.save_json, bg="#007bff", fg="white", font=("Arial", 10, "bold")).grid(row=9, column=0, columnspan=2, pady=10)

    # --- Logic Methods ---
    def load_item_db(self, filename):
        db = {}
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'id\s*:\s*(\d+)\s*,\s*name\s*:\s*["\'](.*?)["\']\s*\}', content)
                for item_id, item_name in matches:
                    db[f"{item_name} ({item_id})"] = int(item_id)
            return db
        except FileNotFoundError: return {}

    def update_suggestions(self, *args):
        search = self.search_var.get().lower()
        self.suggestion_list.delete(0, tk.END)
        if search:
            matches = [n for n in self.item_names if search in n.lower()]
            for m in matches[:10]: self.suggestion_list.insert(tk.END, m)

    def on_select_suggestion(self, event):
        if self.suggestion_list.curselection():
            selection = self.suggestion_list.get(self.suggestion_list.curselection())
            self.selected_id_label.config(text=f"ID: {self.item_map[selection]}")

    def add_item(self, target):
        item_id_text = self.selected_id_label.cget("text").replace("ID: ", "")
        qty = self.qty_entry.get().strip()
        if item_id_text != "None" and qty.isdigit():
            entry = {"itemId": int(item_id_text), "quantity": int(qty)}
            if target == "req":
                self.item_requirements.append(entry)
                self.display_box.insert(tk.END, f"[REQ] {item_id_text} x{qty}")
            else:
                self.item_results.append(entry)
                self.display_box.insert(tk.END, f"[REWARD] {item_id_text} x{qty}")
            self.qty_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Error", "Select an item and enter quantity.")

    def save_json(self):
        name = self.quest_entry.get().strip()
        if not name or not (self.item_requirements or self.item_results):
            messagebox.showerror("Error", "Name and at least one item required.")
            return

        # On s'assure que le Zeny est à la fin des requirements
        reqs = sorted(self.item_requirements, key=lambda x: x['itemId'] == 1)

        new_quest = {
            "name": name,
            "category": self.cat_combo.get(),
            "requirements": reqs,
            "results": self.item_results
        }

        data = []
        if os.path.exists("quests.json"):
            with open("quests.json", "r", encoding='utf-8') as f:
                try: data = json.load(f)
                except: data = []

        data.append(new_quest)

        # Construction manuelle du JSON pour l'indentation hybride
        json_output = "[\n"
        for i, q in enumerate(data):
            # Formatage des requirements (un par ligne, format compact)
            req_lines = ",\n".join([f'      {json.dumps(r)}' for r in q["requirements"]])
            # Formatage des results
            res_lines = ",\n".join([f'      {json.dumps(r)}' for r in q["results"]])

            json_output += "  {\n"
            json_output += f'    "name": "{q["name"]}",\n'
            json_output += f'    "category": "{q["category"]}",\n'
            
            json_output += '    "requirements": [\n' + req_lines + '\n    ],\n' if q["requirements"] else '    "requirements": [],\n'
            json_output += '    "results": [\n' + res_lines + '\n    ]\n' if q["results"] else '    "results": []\n'
            
            json_output += "  }"
            if i < len(data) - 1:
                json_output += ","
            json_output += "\n"
        
        json_output += "]"

        with open("quests.json", "w", encoding='utf-8') as f:
            f.write(json_output)

        messagebox.showinfo("Success", f"Quest '{name}' added to JSON!")
        self.clear_form()

    def clear_form(self):
        #self.quest_entry.delete(0, tk.END)
        self.display_box.delete(0, tk.END)
        self.item_requirements, self.item_results = [], []

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestLoggerApp(root)
    root.mainloop()
