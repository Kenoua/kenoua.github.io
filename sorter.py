import re

def clean_item_db(input_filename, output_filename):
    # Regex to find: id: (numbers), name: "text"
    pattern = re.compile(r'id\s*:\s*(\d+)\s*,\s*name\s*:\s*["\'](.*?)["\']\s*\}')
    
    items = {}

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    item_id = int(match.group(1))
                    item_name = match.group(2)
                    # Using a dictionary automatically removes duplicates
                    # If an ID repeats, the last one found will be kept
                    items[item_id] = item_name

        # Sort the IDs numerically
        sorted_ids = sorted(items.keys())

        # Write the cleaned and sorted data to a new file
        with open(output_filename, 'w', encoding='utf-8') as f:
            for iid in sorted_ids:
                f.write(f'{{ id: {iid} , name: "{items[iid]}" }},\n')
        
        print(f"Success! {len(items)} unique items saved to {output_filename}")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")

# Run the cleaning process
clean_item_db('output.txt', 'cleaned_questItemsDB.txt')
