class Coordinates:
    def __init__(self, x: int | float = 0, y: int | float = 0, w: int | float = 0, h: int | float = 0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return f"Coordinates(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def __reduce__(self):
        return (self.__class__, (self.x, self.y, self.w, self.h))

COORDINATES = {
    (16, 9): {
        (1920, 1080): {
            "terminal": Coordinates(140, 40, 150, 40),
            "shell": Coordinates(1255, 38, 165, 50),
            "offsets": {
                "page": Coordinates(16, 24)
            },
            "scroll": {
                "page": Coordinates(y=-31.25),
                "characters": Coordinates(y=-56),
                "sonata": Coordinates(y=70)
            },
            "scrapers": {
                "weapons": Coordinates(81.5, 191.5),
                "echoes": Coordinates(81.5, 326.5),
                "devItems": Coordinates(81.5, 596.5),
                "resources": Coordinates(81.5, 731.5),
            },
            "items": {
                "start": Coordinates(205, 122, 151, 181),
                "info": Coordinates(1296, 114, 558, 278),
                "description": Coordinates(1296, 114, 558, 820)
            },
            "weapons": {
                "page": Coordinates(200, 50, 130, 40),
                "start": Coordinates(205, 122, 151, 181),
                "name": Coordinates(1305, 116, 545, 55),
                "value": Coordinates(1655, 320, 190, 40),
                "level": Coordinates(1660, 235, 180, 45),
                "rank": Coordinates(1300, 530, 115, 50)
            },
            "echoes": {
                "page": Coordinates(200, 50, 130, 40),
                "start": Coordinates(205, 122, 151, 181),
                "echoCard": Coordinates(1296, 114, 558, 170),
                "sonata": Coordinates(1298, 397, 554, 467),
                "mouseMovement": Coordinates(1576.5, 665.5),
                "fullStatsName": Coordinates(1380, 430, 360, 380),
                "fullStatsValue": Coordinates(1740, 430, 100, 380)
            },
            "achievements": {
                "status": Coordinates(1579, 230, 256, 65),
                "searchBar": Coordinates(388, 149),
                "searchButton": Coordinates(629, 149),
                "achievementsButton": Coordinates(1674, 790),
                "achievementsTab": Coordinates(835, 570),
            },
            "characters": {
                "offsets": {
                    "leftSide": Coordinates(y=136),
                    "rightSide": Coordinates(y=106),
                    "skillPosition": Coordinates(y=255)
                },
                "leftSide": Coordinates(82, 191),
                "rightSide": Coordinates(1814, 203.50),
                "resonatorName": Coordinates(250, 110, 280, 50),
                "resonatorLevel": Coordinates(180, 200, 135, 80),
                "weaponName": Coordinates(257, 126, 273, 34),
                "weaponLevel": Coordinates(255, 160, 110, 35),
                "weaponRank": Coordinates(175, 355, 95, 35),
                "skillClick": Coordinates(460.5, 903),
                "skillLevel": Coordinates(390, 100, 70, 40),
                "skillButton": Coordinates(200, 980, 120, 35),
                "chainClick": Coordinates(1265, 135),
                "chainButton": Coordinates(342, 964, 110, 32),
                "skillPositions": [
                    Coordinates(755, 905),
                    Coordinates(985, 765),
                    Coordinates(1260, 705),
                    Coordinates(1535, 765),
                    Coordinates(1760, 905)
                ],
                "chainPositions": [
                    Coordinates(1395, 140),
                    Coordinates(1565, 305),
                    Coordinates(1640, 535),
                    Coordinates(1565, 765),
                    Coordinates(1400, 935),
                    Coordinates(1170, 995)
                ]
            }
        }
    },
    (16, 10): {
        (1680, 1050): {
            "terminal": Coordinates(125, 32, 150, 40),
            "shell": Coordinates(1100, 35, 145, 40),
            "offsets": {
                "page": Coordinates(16, 24),
                "characters": Coordinates(y=-56),
                "sonata": Coordinates(y=70),
            },
            "scroll": {
                "page": Coordinates(y=-31.70),
                "characters": Coordinates(y=-56),
                "sonata": Coordinates(y=70)
            },
            "scrapers": {
                "weapons": Coordinates(71.5, 167),
                "echoes": Coordinates(71.5, 285),
                "devItems": Coordinates(71.5, 521),
                "resources": Coordinates(71.5, 639),
            },
            "items": {
                "start": Coordinates(180, 104, 130, 162),
                "info": Coordinates(1136, 154, 485, 240),
                "description": Coordinates(1136, 154, 485, 715)
            },
            "weapons": {
                "page": Coordinates(175, 40, 130, 40),
                "start": Coordinates(180, 104, 130, 162),
                "name": Coordinates(1140, 152, 480, 50),
                "value": Coordinates(1430, 330, 190, 40),
                "level": Coordinates(1435, 255, 180, 45),
                "rank": Coordinates(1135, 510, 100, 50)
            },
            "echoes": {
                "page": Coordinates(175, 40, 130, 40),
                "start": Coordinates(180, 104, 130, 162),
                "echoCard": Coordinates(1136, 152, 486, 152),
                "sonata": Coordinates(1135, 400, 486, 408),
                "mouseMovement": Coordinates(1576.5, 665.5),
                "fullStatsName": Coordinates(1200, 420, 320, 380),
                "fullStatsValue": Coordinates(1510, 420, 100, 380)
            },
            "achievements": {
                "status": Coordinates(1579, 197, 256, 65),
                "searchBar": Coordinates(388, 129),
                "searchButton": Coordinates(550, 129),
                "achievementsButton": Coordinates(1465, 690),
                "achievementsTab": Coordinates(735, 570),
            },
            "characters": {
                "offsets": {
                    "leftSide": Coordinates(y=119),
                    "rightSide": Coordinates(y=93.5),
                    "skillPosition": Coordinates(y=220)
                },
                "leftSide": Coordinates(68, 167.5),
                "rightSide": Coordinates(1586.5, 177.5),
                "resonatorName": Coordinates(220, 102, 280, 50),
                "resonatorLevel": Coordinates(160, 180, 135, 80),
                "weaponName": Coordinates(225, 118, 240, 34),
                "weaponLevel": Coordinates(215, 150, 110, 35),
                "weaponRank": Coordinates(143, 320, 93, 35),
                "skillClick": Coordinates(403, 845),
                "skillLevel": Coordinates(340, 95, 70, 40),
                "skillButton": Coordinates(170, 950, 120, 35),
                "chainClick": Coordinates(1109, 174),
                "chainButton": Coordinates(292, 936, 110, 32),
                "skillPositions": [
                    Coordinates(660, 842),
                    Coordinates(864, 722),
                    Coordinates(1103, 667),
                    Coordinates(1342, 722),
                    Coordinates(1545, 842)
                ],
                "chainPositions": [
                    Coordinates(1224, 176),
                    Coordinates(1369, 319),
                    Coordinates(1424, 519),
                    Coordinates(1369, 724),
                    Coordinates(1224, 864),
                    Coordinates(1024, 919)
                ]
            }
        }
    }
}