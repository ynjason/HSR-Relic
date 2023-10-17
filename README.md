# Honkai: Star Rail - Data Scanner and Relic Evaluator

Easily export light cones, relics, and character data from Honkai: Star Rail to JSON format using OCR. Export relics specifically equipeed on characters and evaluate those relics as well.

## Installation

If you haven't already, download and install [Microsoft Visual C++ Redistributable for Visual Studio 2015-2022](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022) (x86 or x64 depending on system).

[Download latest HSR Relic](https://https://github.com/ynjason/HSR-Relic/releases/latest) and then run as administrator (required to simulate keyboard and mouse presses).

## Instructions

Scan information

1. Set in-game resolution to one that has an aspect ratio of 16:9 (e.g. 1920x1080, 1280x720).
2. **In Star Rail, look away from any bright colours.** _Yes, really._ The inventory screen is translucent and bright colours can bleed through to make the text harder to accurately detect and recognize. Looking towards the ground usually works in most cases, as long as the right side of the screen is relatively dark. (Double-check by opening the inventory page and see if the item info on the right contrasts well with the background.) You can skip this step if you're only scanning characters. (not applicable if scanning Character Relics)
3. Open the cellphone menu (ESC menu).
4. Configure the necessary [scanner settings](#scanner-settings-and-configurations) in HSR Relic.
5. Start the scan.
6. Do not move your mouse during the scan process.
7. Once the scan is complete, some additional time may be required to process the data before generating the final JSON file output.

Evaluate Relics

1. Scan Character relics for any amount of characters
  a. make sure that each of the characters have relics equipped in all slots
  b. make sure that each of the characters has relics with rarity 4 or 5 (or they will be skipped)
2. Switch Tab to Evaluate
3. Select downloaded scanned file in input path
4. Start Relic Evaluation

## Scanner settings and configurations

HSR Relic has the following scan options:

- Select whether to scan light cones, relics, and/or characters.
- Set output location for the JSON file.
- Filter light cones and relics based on a minimum rarity or level threshhold.
- Select to scan Character Relics and specify how many characters to scan

## Acknowledgements
The base of this project is on [HSR-Scanner](https://github.com/kel-z/HSR-Scanner), a large majority of the work was done by him. I just added Character Relic scanning and Relic evaluations. Further notes on the scanning part for characters, lightcones and relics can be found on his github
