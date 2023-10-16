import numpy as np
from pyautogui import locate
from helper_functions import preprocess_img, preprocess_main_key, preprocess_sub_key, resource_path, image_to_string
from PIL import Image
from helper_functions import resource_path, preprocess_trace_img
from utils.game_data_helpers import (
    get_character_meta_data,
    get_closest_character_name,
    get_closest_path_name, get_closest_rarity, get_closest_relic_main_stat, get_closest_relic_name, get_closest_relic_sub_stat, get_relic_meta_data,
)
from utils.screenshot import Screenshot


class CharacterRelicScanner:
    NAV_DATA = {
        "16:9": {
            "ascension_start": (0.78125, 0.203),
            "ascension_offset_x": 0.01328,
            "chars_per_scan": 9,
            "char_start": (0.256, 0.065),
            "char_end": (0.744, 0.066),
            "offset_x": 0.055729,
            "details_button": (0.13, 0.143),
            "traces_button": (0.13, 0.315),
            "eidolons_button": (0.13, 0.49),
            "trailblazer": (0.3315, 0.4432, 0.126, 0.1037),
            "relics_button": (0.13, 0.399),
            "relics": [
                (0.387, 0.262),
                (0.594, 0.323),
                (0.453, 0.385),
                (0.504, 0.584),
                (0.354, 0.646),
                (0.565, 0.705)
            ]
        }
    }

    def __init__(
        self, screenshot: Screenshot, logger, interrupt, update_progress
    ) -> None:
        self.interrupt = interrupt
        self.update_progress = update_progress
        self._trailblazer_imgs = [
            Image.open(resource_path("images\\trailblazerm.png")),
            Image.open(resource_path("images\\trailblazerf.png")),
        ]
        self._screenshot = screenshot
        self._logger = logger
        self._trailblazerScanned = False
        self._lock_icon = Image.open(resource_path("images\\lock.png"))
        self._curr_id = 1
        self._relic_id = 1

    def screenshot_stats(self):
        return self._screenshot.screenshot_character_relic_stats()

    def extract_stats_data(self, key, img): 
        if key == "name":
            return image_to_string(
                img, "ABCDEFGHIJKLMNOPQRSTUVWXYZ 'abcedfghijklmnopqrstuvwxyz-", 6
            )
        elif key == "level":
            level = image_to_string(img, "0123456789", 7, True)
            if not level:
                self._logger.emit(
                    f"Relic ID {self._relic_id}: Failed to extract level. Setting to 0."
                ) if self._logger else None
                level = 0
            return int(level)
        elif key == "mainStatKey":
            # img = preprocess_img(img)
            # img.save(f"C:/Users/ynjason/Desktop/otherProjects/HSR-Relic/testImages/test.png")
            return image_to_string(
                img, "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcedfghijklmnopqrstuvwxyz", 7, True, preprocess_main_key
            )
        elif key == "mainStatVal":
            val = image_to_string(img, "0123456789.%", 7)
            percent = False
            if not val:
                val = image_to_string(img, "0123456789.%", 6)

            if not val or val == ".":
                self._logger.emit(
                    f"Relic ID {self._relic_id}: Failed to get value for main-stat. Either it doesn't exist or the OCR failed."
                ) if self._logger else None
                return tuple([0, False])
            if val[-1] == "%":
                if "." not in val:
                    val = image_to_string(img, "0123456789.%", 7, True, preprocess_main_key)
                val = float(val[:-1])
                percent = True
            else:
                try:
                    val = int(val)
                except ValueError:
                    return tuple([0, False])
            return tuple([val, percent==True])
        elif key == "rarity":
            # Get rarity by color matching
            rarity_sample = np.array(img)
            rarity_sample = rarity_sample[int(rarity_sample.shape[0] / 2)][
                int(rarity_sample.shape[1] / 2)
            ]
            return get_closest_rarity(rarity_sample)
        else:
            return img

    def parse(self, stats_dict):
        if self.interrupt.is_set():
            return

        character = {
            "key": stats_dict["name"].split("#")[0],
            "relics": []
        }

        for relic in stats_dict["relics"]:
            parsed_relic = {}
            for key in relic:
                parsed_relic[key] = self.extract_stats_data(key, relic[key])
            if parsed_relic["mainStatVal"][1] == True:
                parsed_relic["mainStatVal"] = parsed_relic["mainStatVal"][0]
                parsed_relic["mainStatKey"] += "_"
            else:
                parsed_relic["mainStatVal"] = parsed_relic["mainStatVal"][0]

            name = parsed_relic["name"]
            level = parsed_relic["level"]
            mainStatKey = parsed_relic["mainStatKey"]
            mainStatVal = parsed_relic["mainStatVal"]
            lock = parsed_relic["lock"]
            rarity = parsed_relic["rarity"]

            # Fix OCR errors
            name, _ = get_closest_relic_name(name)
            mainStatKey, _ = get_closest_relic_main_stat(mainStatKey)

            if mainStatKey == "":
                self._logger.emit(
                    f"Relic ID {self._relic_id}: Failed to get value for main stat. Either it doesn't exist or the OCR failed."
                ) if self._logger else None

            # Parse sub-stats
            subStats = []
            for i in range(1, 5):
                key = parsed_relic["subStatKey_" + str(i)]

                key = image_to_string(
                    key, "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcedfghijklmnopqrstuvwxyz", 7, True, preprocess_sub_key
                )
                if not key:
                    # self._logger.emit(
                    #     f"Relic ID {self._curr_id}: Failed to get key. Either it doesn't exist or the OCR failed.") if self._logger else None
                    print("here1")
                    break
                key, min_dist = get_closest_relic_sub_stat(key)
                if min_dist > 5:
                    print("here2")
                    break

                val_img = parsed_relic["subStatVal_" + str(i)]
                val = image_to_string(val_img, "0123456789.%", 7, True, preprocess_sub_key)
                if not val:
                    val = image_to_string(val_img, "0123456789.%", 6, True, preprocess_sub_key)

                if not val or val == ".":
                    if min_dist == 0:
                        self._logger.emit(
                            f"Relic ID {self._relic_id}: Failed to get value for sub-stat: {key}. Either it doesn't exist or the OCR failed."
                        ) if self._logger else None
                    print("here3")
                    break

                if val[-1] == "%":
                    if "." not in val:
                        val = image_to_string(val_img, "0123456789.%", 7, True, preprocess_sub_key)
                    val = float(val[:-1])
                    key += "_"
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        print("here4")
                        # self._logger.emit(
                        #     f"Relic ID {self._curr_id}: Error parsing sub-stat value: {val}.") if self._logger else None
                        break

                subStats.append({"key": key, "value": val})

            metadata = get_relic_meta_data(name)
            setKey = metadata["setKey"]
            slotKey = metadata["slotKey"]

            # Check if locked by image matching
            min_dim = min(lock.size)
            lock_img = self._lock_icon.resize((min_dim, min_dim))
            lock = locate(lock_img, lock, confidence=0.1) is not None

            result = {
                "setKey": setKey,
                "slotKey": slotKey,
                "rarity": rarity,
                "level": level,
                "mainStatKey": mainStatKey,
                "mainStatVal": mainStatVal,
                "subStats": subStats,
                "lock": lock,
                "_id": f"relic_{self._relic_id}",
            }
            self._relic_id += 1

            character["relics"].append(result)

        if self.update_progress:
            self.update_progress.emit(102)

        return character

    def get_closest_name_and_path(self, character_name, path):
        path, _ = get_closest_path_name(path)

        if self.__is_trailblazer():
            if self._trailblazerScanned:
                self._logger.emit(
                    "WARNING: Parsed more than one Trailblazer. Please review JSON output."
                ) if self._logger else None
            else:
                self._trailblazerScanned = True

            return "Trailblazer" + path.split(" ")[-1], path
        else:
            character_name, min_dist = get_closest_character_name(character_name)

            if min_dist > 5:
                raise Exception(
                    f"Character not found in database. Got {character_name}"
                )

            return character_name, path

    def __is_trailblazer(self):
        char = self._screenshot.screenshot_character()
        for trailblazer in self._trailblazer_imgs:
            trailblazer = trailblazer.resize(char.size)
            if locate(char, trailblazer, confidence=0.8) is not None:
                return True

        return False
