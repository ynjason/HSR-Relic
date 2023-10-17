import json
import numpy as np
import asyncio
from helper_functions import resource_path

class HSRRelicEvaluator:
    update_progress = None
    logger = None
    interrupt = asyncio.Event()

    def __init__(self, config):
        self._config = config
        with open(resource_path("utils/evaluate_stats.json"), "r") as infile:
            self._possible_stats = json.loads(infile.read())
        with open(resource_path("utils/character_relic_weights.json"), "r") as infile:
            self._character_relic_weights = json.loads(infile.read())

        self.interrupt.clear()

    async def start_evaluation(self):
        input_path = self._config["relic_evaluate_input_path"]
        with open(input_path, "r") as infile:
            input_map = json.loads(infile.read())

        # self._max_possible_stat = 0
        # for _, val in self._character_relic_weights.items():
        #     self._max_possible_stat = max(self._max_possible_stat, sum(val["max_effective_stat"].values()))
        #     print(self._max_possible_stat)
        
        evaluation = {}
        for character in input_map["character_relics"]:
            char_name = character["key"]
            evaluation[char_name] = []
            for relic in character["relics"]:
                evaluation[char_name].append(self.evaluate_relic(relic, char_name))

        if self.interrupt.is_set():
            return

        return {
            "source": "HSR_Relic",
            "version": 1,
            "evaluation": evaluation
        }

    def evaluate_relic(self, relic, char_name):
        effective_stats = self._character_relic_weights[char_name]["stat_weights"]
        max_possible_stat = sum([x for x in self._character_relic_weights[char_name]["max_effective_stat"].values()])
        max_effective_stat = self._character_relic_weights[char_name]["max_effective_stat"][relic["slotKey"]]
        relic_sets = self._character_relic_weights[char_name]["relic_sets"]
        rarity = relic["rarity"]

        # If relic is not rarity 4 or 5 then skip
        if rarity not in ["4", "5"]:
            return relic

        total_effective_stats = 0
        if relic["slotKey"] in ["Body", "Feet", "Planar Sphere", "Link Rope"]:
            if relic["mainStatKey"] in effective_stats and effective_stats[relic["mainStatKey"]] > 0:
                total_effective_stats += 3 * effective_stats[relic["mainStatKey"]]
        for subStat in relic["subStats"]:
            sub_stat_key = subStat["key"]
            sub_stat_value = subStat["value"]
            sub_stat_map = self._possible_stats["sub"][str(rarity)][sub_stat_key]
            if str(sub_stat_value) in sub_stat_map:
                total_effective_stats += sub_stat_map[str(sub_stat_value)] * effective_stats.get(sub_stat_key, 0)
            else:
                sub_stat_key_array = np.asarray([float(x) for x in sub_stat_map.keys()])
                idx = (np.abs(sub_stat_key_array - sub_stat_value)).argmin()
                total_effective_stats += sub_stat_map[str(sub_stat_key_array[idx])] * effective_stats.get(sub_stat_key, 0)
        total_effective_stats = min(max_effective_stat, total_effective_stats)
        score = (max_possible_stat / max_effective_stat) * total_effective_stats
        score_value = self.determine_score_value(score)
        correct_relic_set = relic["setKey"] in relic_sets

        relic["total_effective_stats"] = total_effective_stats
        relic["score"] = score
        relic["score_value"] = score_value
        relic["correct_relic_set"] = correct_relic_set
        
        return relic

    def determine_score_value(self, score):
        if score > 50.9:
            return "OP"
        elif score > 42.9 and score <= 50.9:
            return "SSS"
        elif score > 37.2 and score <= 42.9:
            return "SS"
        elif score > 32.8 and score <= 37.2:
            return "S"
        elif score > 28.4 and score <= 32.8:
            return "A"
        elif score > 22.6 and score <= 28.4:
            return "B"
        elif score > 17.5 and score <= 22.6:
            return "C"
        elif score > 13.6 and score <= 17.5:
            return "D"
        else:
            return "N/A"

    def stop_evaluation(self):
        self.interrupt.set()
