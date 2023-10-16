# import pyautogui
import win32gui
from PIL import Image, ImageGrab


class Screenshot:
    # each tuple is (x0, y0, x1, y1) in % of the window size
    # otherwise, x1 and y1 are hardcoded
    coords = {
        "16:9": {
            "quantity": (0.46, 0.89, 0.13, 0.06),
            "stats": (0.72, 0.09, 0.25, 0.78),
            "character_relic_stats": (0.76, 0.09, 0.24, 0.78),
            "sort": (0.079, 0.9, 0.07, 0.033),
            "character": {
                "count": (0.56, 0.555, 0.05, 0.035),
                "chest": (0.44, 0.3315, 0.1245, 0.1037),
                "name": (0.0656, 0.059, 0.16, 0.0314),
                "level": (0.795, 0.216, 0.024, 0.034),
                "eidolons": [
                    (0.198, 0.34),
                    (0.187, 0.546),
                    (0.377, 0.793),
                    (0.826, 0.679),
                    (0.796, 0.43),
                    (0.716, 0.197),
                ],
                "traces": {
                    "hunt": {
                        "basic": (0.502171875, 0.5347222222222222),
                        "skill": (0.65546875, 0.5347222222222222),
                        "ult": (0.579296875, 0.6006944444444444),
                        "talent": (0.579296875, 0.4625),
                    },
                    "erudition": {
                        "basic": (0.5076875, 0.5888888888888889),
                        "skill": (0.651171875, 0.5888888888888889),
                        "ult": (0.579296875, 0.5888888888888889),
                        "talent": (0.579296875, 0.4395833333333333),
                    },
                    "harmony": {
                        "basic": (0.508203125, 0.5493055555555556),
                        "skill": (0.6505625, 0.5493055555555556),
                        "ult": (0.579078125, 0.6458333333333334),
                        "talent": (0.579078125, 0.5243055555555556),
                    },
                    "preservation": {
                        "basic": (0.503515625, 0.6076388888888888),
                        "skill": (0.653125, 0.6069444444444444),
                        "ult": (0.577734375, 0.5881944444444445),
                        "talent": (0.578125, 0.4625),
                    },
                    "destruction": {
                        "basic": (0.491796875, 0.56875),
                        "skill": (0.6640625, 0.56875),
                        "ult": (0.577734375, 0.5888888888888889),
                        "talent": (0.577734375, 0.4625),
                    },
                    "nihility": {
                        "basic": (0.498046875, 0.5173611111111112),
                        "skill": (0.658984375, 0.5173611111111112),
                        "ult": (0.57734375, 0.5048611111111111),
                        "talent": (0.57734375, 0.3875),
                    },
                    "abundance": {
                        "basic": (0.506640625, 0.5673611111111111),
                        "skill": (0.651953125, 0.5673611111111111),
                        "ult": (0.5796875, 0.59375),
                        "talent": (0.5796875, 0.4625),
                    },
                },
            },
            # % of the stats screenshot
            "light_cone": {
                "name": (0, 0, 1, 0.09),
                "level": (0.13, 0.32, 0.35, 0.37),
                "superimposition": (0.53, 0.48, 0.6, 0.55),
                "equipped": (0.45, 0.95, 0.68, 1),
                "equipped_avatar": (0.35, 0.94, 0.44, 0.99),
                "lock": (0.896, 0.321, 0.97, 0.365),
            },
            "relic": {
                "name": (0, 0, 1, 0.09),
                "level": (0.115, 0.255, 0.23, 0.3),
                "lock": (0.865, 0.253, 0.935, 0.293),
                "rarity": (0.07, 0.15, 0.2, 0.22),
                "equipped": (0.45, 0.95, 0.68, 1),
                "equipped_avatar": (0.35, 0.94, 0.44, 0.99),
                "mainStatKey": (0.115, 0.358, 0.7, 0.4),
                "subStatKey_1": (0.115, 0.41, 0.77, 0.45),
                "subStatVal_1": (0.77, 0.41, 1, 0.45),
                "subStatKey_2": (0.115, 0.45, 0.77, 0.5),
                "subStatVal_2": (0.77, 0.45, 1, 0.5),
                "subStatKey_3": (0.115, 0.495, 0.77, 0.542),
                "subStatVal_3": (0.77, 0.495, 1, 0.542),
                "subStatKey_4": (0.115, 0.545, 0.77, 0.595),
                "subStatVal_4": (0.77, 0.545, 1, 0.595),
            },
            "character_relic": {
                "name": (0, 0.08, 0.85, 0.14),
                "level": (0.80, 0.136, 0.92, 0.169),
                "lock": (0.858, 0.091, 0.909, 0.124),
                "rarity": (0.026, 0.191, 0.036, 0.218),
                "mainStatKey": (0.152, 0.214, 0.74, 0.257),
                "mainStatVal": (0.74, 0.214, 0.912, 0.257),
                "subStatKey_1": (0.152, 0.263, 0.74, 0.307),
                "subStatVal_1": (0.74, 0.263, 0.912, 0.307),
                "subStatKey_2": (0.152, 0.313, 0.74, 0.357),
                "subStatVal_2": (0.74, 0.313, 0.912, 0.357),
                "subStatKey_3": (0.152, 0.363, 0.74, 0.407),
                "subStatVal_3": (0.74, 0.363, 0.912, 0.407),
                "subStatKey_4": (0.152, 0.409, 0.74, 0.453),
                "subStatVal_4": (0.74, 0.409, 0.912, 0.453),
            },
        }
    }

    def __init__(self, hwnd, aspect_ratio="16:9"):
        self._aspect_ratio = aspect_ratio

        self._window_width, self._window_height = win32gui.GetClientRect(hwnd)[2:]
        self._window_x, self._window_y = win32gui.ClientToScreen(hwnd, (0, 0))

        self._x_scaling_factor = self._window_width / 1920
        self._y_scaling_factor = self._window_height / 1080

    def screenshot_screen(self):
        return self.__take_screenshot(0, 0, 1, 1)

    def screenshot_light_cone_stats(self):
        return self.__screenshot_stats("light_cone")

    def screenshot_relic_stats(self):
        return self.__screenshot_stats("relic")
        
    def screenshot_character_relic_stats(self):
        return self.__screenshot_stats("character_relic", "character_relic_stats")

    def screenshot_relic_sort(self):
        coords = self.coords[self._aspect_ratio]["sort"]
        coords = (coords[0] + 0.035, coords[1], coords[2], coords[3])
        return self.__take_screenshot(*coords)

    def screenshot_light_cone_sort(self):
        return self.__take_screenshot(*self.coords[self._aspect_ratio]["sort"])

    def screenshot_quantity(self):
        return self.__take_screenshot(*self.coords[self._aspect_ratio]["quantity"])

    def screenshot_character_count(self):
        return self.__take_screenshot(
            *self.coords[self._aspect_ratio]["character"]["count"]
        )

    def screenshot_character_name(self):
        return self.__take_screenshot(
            *self.coords[self._aspect_ratio]["character"]["name"]
        )

    def screenshot_character_level(self):
        return self.__take_screenshot(
            *self.coords[self._aspect_ratio]["character"]["level"]
        )

    def screenshot_character(self):
        return self.__take_screenshot(
            *self.coords[self._aspect_ratio]["character"]["chest"]
        )

    def screenshot_character_eidolons(self):
        res = []

        screenshot = ImageGrab.grab(all_screens=True)
        offset, _, _ = Image.core.grabscreen_win32(False, True)
        x0, y0 = offset

        for c in self.coords[self._aspect_ratio]["character"]["eidolons"]:
            left = self._window_x + int(self._window_width * c[1])
            upper = self._window_y + int(self._window_height * c[0])
            right = left + self._window_width * 0.018
            lower = upper + self._window_height * 0.0349
            res.append(screenshot.crop((left - x0, upper - y0, right - x0, lower - y0)))

        return res

    def screenshot_character_hunt_traces(self):
        return self.__screenshot_traces("hunt")

    def screenshot_character_erudition_traces(self):
        return self.__screenshot_traces("erudition")

    def screenshot_character_harmony_traces(self):
        return self.__screenshot_traces("harmony")

    def screenshot_character_preservation_traces(self):
        return self.__screenshot_traces("preservation")

    def screenshot_character_destruction_traces(self):
        return self.__screenshot_traces("destruction")

    def screenshot_character_nihility_traces(self):
        return self.__screenshot_traces("nihility")

    def screenshot_character_abundance_traces(self):
        return self.__screenshot_traces("abundance")

    def __take_screenshot(self, x, y, width, height):
        # adjust coordinates to window
        x = self._window_x + int(self._window_width * x)
        y = self._window_y + int(self._window_height * y)
        width = int(self._window_width * width)
        height = int(self._window_height * height)

        # screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot = ImageGrab.grab(
            bbox=(x, y, x + width, y + height), all_screens=True
        )
        # print(width, height, width / self._x_scaling_factor, height / self._y_scaling_factor)
        screenshot = screenshot.resize(
            (int(width / self._x_scaling_factor), int(height / self._y_scaling_factor))
        )
        return screenshot

    def __screenshot_stats(self, key, stats_type = "stats"):
        coords = self.coords[self._aspect_ratio]

        img = self.__take_screenshot(*coords[stats_type])

        adjusted_stat_coords = {
            k: tuple(
                [
                    int(v * img.width) if i % 2 == 0 else int(v * img.height)
                    for i, v in enumerate(v)
                ]
            )
            for k, v in coords[key].items()
        }

        res = {k: img.crop(v) for k, v in adjusted_stat_coords.items()}

        if stats_type == "character_relic_stats":
            screen = self.screenshot_screen()
            adjusted_coords = tuple(
                [
                    int(v * screen.width) if i % 2 == 0 else int(v * screen.height)
                    for i, v in enumerate(coords["character_relic"]["rarity"])
                ]
            )
            res["rarity"] = screen.crop(adjusted_coords)


        # for i, image in res.items():
        #     image.save(f"C:/Users/ynjason/Desktop/otherProjects/HSR-Relic/testImages/{i}.png")

        return res

    def __screenshot_traces(self, key):
        coords = self.coords[self._aspect_ratio]

        res = {"levels": {}, "unlocks": {}}

        screenshot = ImageGrab.grab(all_screens=True)
        offset, _, _ = Image.core.grabscreen_win32(False, True)
        x0, y0 = offset

        for k, v in coords["character"]["traces"][key].items():
            left = self._window_x + int(self._window_width * v[0])
            upper = self._window_y + int(self._window_height * v[1])
            right = left + int(self._window_width * 0.04)
            lower = upper + int(self._window_height * 0.028)

            res["levels"][k] = screenshot.crop(
                (left - x0, upper - y0, right - x0, lower - y0)
            )

        return res
