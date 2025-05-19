# WuWa Inventory Kamera - A Wuthering Waves Data Scanner

WuWa Inventory Kamera is a tool designed to scan and manage data for the game Wuthering Waves.  
The data format is specifically designed for [WuWa Tracker](https://wuwatracker.com), facilitating importing data. *(Please note that I am not affiliated with WuWa Tracker.)*

## Supported Features
*Note: This tool currently works __only__ in full-screen mode.*

- **Supported Screens:**
  - 1680x1050
  - 1920x1080
  - 2560x1440
  - (other resolutions not tested; may not be compatible)

- **Supported Languages:**
  - All (tested only with English)

- **Features:**
  - Scan Characters
  - Scan Weapons
  - Scan Echoes
  - Scan Development Items
  - Scan Resources
  - Scan Achievements
  - Edit/View inventory data

## To-Do List
- [x] Character Scanner (no echo)
- [x] Weapons Scanner
- [x] Echoes Scanner
- [x] Achievements Scanner
- [ ] Auto Updater
- [x] Support for additional in-game languages
- [ ] Support for more software languages
- [x] Improve text recognition accuracy
- [ ] Improve logs
- [x] Optimize releases size
- [ ] Rewrite the code (after all tasks are complete)

## Tutorial

1. **Prepare for Scanning**
   - Ensure you are in the correct menu before clicking on 'Start Scanning'. This is crucial for accurate data capture.  
   ![menu](https://telegra.ph/file/12abde4d5ffdfb68c0142.png)

2. **Complete the Scanning Process**
   - Once scanning is complete, open WuWa Inventory Kamera. You should see something similar to the image below:  
   ![complete](https://telegra.ph/file/a50eba86bcb813e82b919.png)

3. **(Optional) Review Scanned Data**
   - You can optionally check the data that has been scanned to ensure everything is captured correctly:  
   ![review](https://telegra.ph/file/f6c6f2790eb23aa7ce3b5.png)

## Data

<details>
  <summary>inventory.json</summary>

  ```json
  {
    "_comment": "itemID: string(int), quantity: int",
    "2": 234
  }
  ```
</details>

<details>
  <summary>characters.json</summary>

  ```json
  {
    "_comment": "resonatorID(1205): string(int), if not the OCR failed and you will see a flatcase name of that",
    "1205": {
      "level": 90,
      "ascension": 6,
      "weapon": {
        "_comment": "weaponID: int, if not the OCR failed and you will see a flatcase name of that",
        "id": 21020064,
        "level": 80,
        "ascension": 5,
        "rank": 1
      },
      "echoes": {},
      "skills": {
        "normal": 10,
        "resonance": 10,
        "forte": 10,
        "liberation": 10,
        "intro": 10,
        "stats0": 2,
        "stats1": 2,
        "inherent": 2,
        "stats3": 2,
        "stats4": 2
      },
      "chain": 0
    }
  }
  ```
</details>

<details>
  <summary>weapons.json</summary>

  ```json
  [
    {
      "_comment": "weaponID(21030016): string(int), if not the OCR failed and you will see a flatcase name of that",
      "21030016": {
        "level": 50,
        "ascension": 2,
        "rank": 1
      }
    }
  ]
  ```
</details>

<details>
  <summary>echoes.json</summary>

  ```json
  [
    {
      "_comment": "monsterID(340000070): string(int), if not the OCR failed and you will see a flatcase name of that",
      "340000070": {
        "_comment": "sonata: is always flatcase",
        "level": 25,
        "tuneLv": 5,
        "sonata": "havoceclipse",
        "rarity": 5,
        "stats": {
          "main": {
            "cr%": 22.0,
            "atk": 150
          },
          "sub": {
            "atk": 40,
            "def": 50,
            "hp": 470,
            "basicAttack%": 8.6
          }
        }
      }
    }
  ]
  ```
  <details>
    <summary>Echo stats</summary>


  ```json
  {
    "_comment": "% will automatically be added to the stats if it is a percentage",
    "hp": "hp",
    "atk": "atk",
    "critrate": "cr",
    "critdmg": "cd",
    "def": "def",
    "energyregen": "er",
    "resonanceskilldmgbonus": "skillDmg",
    "basicattackdmgbonus": "basicAttack",
    "heavyattackdmgbonus": "heavyAttack",
    "resonanceliberationdmgbonus": "liberationDmg",
    "glaciodmgbonus": "glacio",
    "fusiondmgbonus": "fusion",
    "electrodmgbonus": "electro",
    "aerodmgbonus": "aero",
    "spectrodmgbonus": "spectro",
    "havocdmgbonus": "havoc",
    "healingbonus": "healing"
  }
  ```
  </details>
</details>

## Credits
- Highly inspired by [Inventory Kamera](https://github.com/Andrewthe13th/Inventory_Kamera) created by [Andrewthe13th](https://github.com/Andrewthe13th)
- Item IDs sourced from [Dimbreath](https://github.com/Dimbreath/WutheringData)
- Assets sourced from [Stormy Waves](https://github.com/Stormy-Waves/WW_Icon)

## License
This project is licensed under the [GNU General Public License (GPL) v3](https://www.gnu.org/licenses/gpl-3.0.html).  
This means you are free to use, modify, and distribute the project, but you must keep it under the same license and provide proper attribution.

### Third-Party Libraries
This project uses third-party libraries and resources that may be distributed under different licenses. Please check the respective library documentation for details.

## Disclaimer
All rights reserved by © Guangzhou Kuro Technology Co., Ltd. This project is not affiliated with nor endorsed by Kuro Games. Wuthering Waves and other properties are trademarks of their respective owners.
