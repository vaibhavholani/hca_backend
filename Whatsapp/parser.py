from fuzzywuzzy import process
from API_Database import get_all_names_ids

MATCH_THRESHOLD = 80

def find_closest_match(query):
    suppliers = get_all_names_ids('supplier')
    supplier_dict = {supplier["name"]: {"id": supplier["id"], "type": "supplier"} for supplier in suppliers}

    parties = get_all_names_ids('party')
    party_dict = {party["name"]: {"id": party["id"], "type": "party"} for party in parties}

    combined_dict = {**supplier_dict, **party_dict}
    choices = list(combined_dict.keys())

    matches = process.extract(query, choices, limit=5)

    # Attach IDs, types to the top 5 matches and filter for scores > 80
    matches_with_details = [
        {
            "name": match[0], 
            "score": match[1], 
            "id": combined_dict[match[0]]["id"], 
            "type": combined_dict[match[0]]["type"]
        } 
        for match in matches if match[1] > MATCH_THRESHOLD
    ]

    # Separate matches into suppliers and parties
    supplier_matches = [match for match in matches_with_details if match["type"] == "supplier"]
    party_matches = [match for match in matches_with_details if match["type"] == "party"]

    return {"suppliers": supplier_matches, "parties": party_matches}
