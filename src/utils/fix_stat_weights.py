import json

from generate_evaluate_json import resource_path

def generate_json():
    with open(resource_path("character_relic_weights.json"), "r") as infile:
            stat_weights = json.loads(infile.read())
    for _, char in stat_weights.items():
        char["stat_weights"]["HP"] =  char["stat_weights"]["HP_"]
        char["stat_weights"]["ATK"] =  char["stat_weights"]["ATK_"]
        char["stat_weights"]["DEF"] =  char["stat_weights"]["DEF_"]
    json_object = json.dumps(stat_weights, indent=2)
    with open(resource_path("character_relic_weights.json"), "w") as outfile:
        outfile.write(json_object)

if __name__ == "__main__":
    generate_json()