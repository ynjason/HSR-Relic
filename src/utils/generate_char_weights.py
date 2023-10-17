import json

from game_data_helpers import CHARACTER_KEYS, RELIC_META_DATA
from generate_evaluate_json import resource_path

relic_stats = [
    "HP_",
    "ATK_",
    "DEF_",
    "SPD",
    "CRIT Rate_",
    "CRIT DMG_",
    "Break Effect_",
    "Outgoing Healing Boost_",
    "Energy Regeneration Rate_",
    "Effect Hit Rate_",
    "Effect RES_",
    "Physical DMG Boost_",
    "Fire DMG Boost_",
    "Ice DMG Boost_",
    "Wind DMG Boost_",
    "Lightning DMG Boost_",
    "Quantum DMG Boost_",
    "Imaginary DMG Boost_"
]

relic_types = [
    "Head",
    "Hand",
    "Body",
    "Feet",
    "Link Rope",
    "Planar Sphere"
]

relic_sets = set([val["setKey"] for _, val in RELIC_META_DATA.items()])

def generate_json():
    merged_json = {}
    for char_name in CHARACTER_KEYS:
        merged_json[char_name] = {}
        merged_json[char_name]["stat_weights"] = {}
        for stat in relic_stats:
            merged_json[char_name]["stat_weights"][stat] = 0
        merged_json[char_name]["max_effective_stat"] = {}
        for relic_type in relic_types:
            merged_json[char_name]["max_effective_stat"][relic_type] = 8
        merged_json[char_name]["relic_sets"] = list(relic_sets)
    json_object = json.dumps(merged_json, indent=2)
    with open(resource_path("character_relic_weights2.json"), "w") as outfile:
        print(json_object)
        outfile.write(json_object)

if __name__ == "__main__":
    generate_json()