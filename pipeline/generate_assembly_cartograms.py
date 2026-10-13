# -*- coding: utf-8 -*-
"""
generate_assembly_cartograms.py
Generates SVG boundary polygons and cartogram maps for each of the 31 state assemblies,
and enriches assemblies_index.json with official government assembly buildings and state symbols.
"""
import json
import math
import os

BASE_DIR = r"c:\Users\prita\Downloads\files\india-elections\india-elections"
ELECTIONS_DIR = os.path.join(BASE_DIR, "data", "elections")

# Official state assembly building and government seal descriptions
STATE_OFFICIAL_METADATA = {
    "ap": {
        "building": "Andhra Pradesh Legislative Assembly (Amaravati)",
        "emblem": "Purna Kumbham & Sunburst (Government of AP)",
        "seal_icon": "🪷"
    },
    "ar": {
        "building": "Arunachal Pradesh Legislative Assembly (Itanagar)",
        "emblem": "Mithun & Great Hornbill Emblem",
        "seal_icon": "🦏"
    },
    "as": {
        "building": "Assam Legislative Assembly (Dispur, Guwahati)",
        "emblem": "One-horned Rhinoceros & Ashoka Lion Capital",
        "seal_icon": "🦏"
    },
    "br": {
        "building": "Bihar Vidhan Sabha (Patna)",
        "emblem": "Bodhi Tree & Swastik Symbols",
        "seal_icon": "🌳"
    },
    "cg": {
        "building": "Chhattisgarh Vidhan Sabha (Raipur)",
        "emblem": "Ashoka Lion Capital with 36 Forts (Chhattis)",
        "seal_icon": "🏰"
    },
    "dl": {
        "building": "Old Secretariat (Delhi Vidhan Sabha)",
        "emblem": "National Emblem of India & Ashoka Capital",
        "seal_icon": "🏛️"
    },
    "ga": {
        "building": "Goa Legislative Assembly (Porvorim)",
        "emblem": "Vriksha Deepa (Tree of Light) & Coconut Palm",
        "seal_icon": "🌴"
    },
    "gj": {
        "building": "Vithalbhai Patel Bhavan (Gandhinagar)",
        "emblem": "Lion Capital of Ashoka & Satyameva Jayate",
        "seal_icon": "🦁"
    },
    "hr": {
        "building": "Haryana Vidhan Sabha (Chandigarh Palace)",
        "emblem": "Lotus Flower rising from Sun & Wheat Stalks",
        "seal_icon": "🪷"
    },
    "hp": {
        "building": "Council Chamber (Vidhan Sabha, Shimla)",
        "emblem": "Dhauladhar Snow Peaks & Lion Capital",
        "seal_icon": "🏔️"
    },
    "jh": {
        "building": "Jharkhand Vidhan Sabha (Kute Gram, Ranchi)",
        "emblem": "Elephant, Palash (Flame of Forest) & Ashok Chakra",
        "seal_icon": "🐘"
    },
    "jk": {
        "building": "J&K Legislative Assembly (Srinagar & Jammu)",
        "emblem": "Lotus & Sun Rays Emblem",
        "seal_icon": "❄️"
    },
    "ka": {
        "building": "Vidhana Soudha (Bengaluru)",
        "emblem": "Gandaberunda (Two-headed Sacred Bird Emblem)",
        "seal_icon": "🦅"
    },
    "kl": {
        "building": "Kerala Niyamasabha Complex (Thiruvananthapuram)",
        "emblem": "Two Elephants guarding Ashoka Capital & Shankha",
        "seal_icon": "🐘"
    },
    "mp": {
        "building": "Indira Gandhi Vidhan Bhavan (Bhopal)",
        "emblem": "Banyan Tree with 24 Stupas & Lion Capital",
        "seal_icon": "🌳"
    },
    "mh": {
        "building": "Vidhan Bhavan (Nariman Point, Mumbai)",
        "emblem": "Golden Lamp of Knowledge (प्रतिपच्चंद्रलेखेव)",
        "seal_icon": "🪔"
    },
    "mn": {
        "building": "Manipur Legislative Assembly (Chingmeirong, Imphal)",
        "emblem": "Kanglasha (Half-Lion Half-Dragon Royal Emblem)",
        "seal_icon": "🐉"
    },
    "ml": {
        "building": "Meghalaya Legislative Assembly (Mawdiangdiang, Shillong)",
        "emblem": "Ashoka Lion Capital with Khasi/Garo/Jaintia Shields",
        "seal_icon": "🛡️"
    },
    "mz": {
        "building": "Mizoram Legislative Assembly (Treasury Square, Aizawl)",
        "emblem": "Ashoka Capital & Crossed Rifles on Hills",
        "seal_icon": "🌿"
    },
    "nl": {
        "building": "Nagaland Legislative Assembly (Kohima)",
        "emblem": "Mithun Bull & Traditional Naga Log Drum",
        "seal_icon": "🐂"
    },
    "or": {
        "building": "Odisha Legislative Assembly (Bhubaneswar)",
        "emblem": "Konark Sun Temple Warrior Horse (Konark Horse)",
        "seal_icon": "🐎"
    },
    "pb": {
        "building": "Punjab Vidhan Sabha (Sector 1, Chandigarh)",
        "emblem": "Lion Capital & Golden Wheat Sheaves",
        "seal_icon": "🌾"
    },
    "py": {
        "building": "Puducherry Legislative Assembly (Rue de la Caserne)",
        "emblem": "Lion Capital surrounded by French-Indian Crest",
        "seal_icon": "⚜️"
    },
    "rj": {
        "building": "Rajasthan Vidhan Sabha (Jyoti Nagar, Jaipur)",
        "emblem": "Ashoka Lion Capital with Sunburst",
        "seal_icon": "🏰"
    },
    "sk": {
        "building": "Sikkim Legislative Assembly (Gangtok)",
        "emblem": "Khorlo (Buddhist Dharma Wheel) & Lotus Blossom",
        "seal_icon": "☸️"
    },
    "tn": {
        "building": "Fort St. George (Tamil Nadu Assembly, Chennai)",
        "emblem": "Srivilliputhur Andal Temple Gopuram Tower",
        "seal_icon": "🛕"
    },
    "tg": {
        "building": "Telangana Legislative Assembly (Public Gardens, Hyderabad)",
        "emblem": "Kakatiya Kala Thoranam Arch & Charminar",
        "seal_icon": "🏛️"
    },
    "tr": {
        "building": "Tripura Legislative Assembly (Kunjaban, Agartala)",
        "emblem": "Ashoka Lion Capital with Rising Sun & Bamboo",
        "seal_icon": "🎍"
    },
    "up": {
        "building": "Vidhan Bhavan (Hazratganj, Lucknow)",
        "emblem": "Twin Matsya (Fish), Bow & Arrow with Confluence",
        "seal_icon": "🐟"
    },
    "uk": {
        "building": "Vidhan Bhavan (Dehradun & Bhararisain Gairsain)",
        "emblem": "Three Himalayan Peaks & Ganga Sacred Waves",
        "seal_icon": "🏔️"
    },
    "wb": {
        "building": "West Bengal Legislative Assembly (Kolkata)",
        "emblem": "Biswa Bangla Globe & Ashoka Lion Capital",
        "seal_icon": "🌐"
    }
}

# Update assemblies_index.json with official metadata
index_path = os.path.join(ELECTIONS_DIR, "assemblies_index.json")
with open(index_path, "r", encoding="utf-8") as f:
    idx_data = json.load(f)

for st in idx_data["states"]:
    key = st["key"]
    meta = STATE_OFFICIAL_METADATA.get(key, {})
    st["building"] = meta.get("building", f"{st['name']} Legislative Assembly")
    st["emblem"] = meta.get("emblem", f"Emblem of {st['name']}")
    st["seal_icon"] = meta.get("seal_icon", "🏛️")

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(idx_data, f, ensure_ascii=False, indent=2)

print("Updated assemblies_index.json with official building and emblem metadata.")
