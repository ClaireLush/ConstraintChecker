class GridRef:
    def __init__(self, easting, northing):
        self.easting = easting
        self.northing = northing

    def getGridRef(self):
        eastingStr = str(self.easting)
        eastingLen = len(eastingStr)
        if eastingLen > 14:
            eastingLen = 14

        northingStr = str(self.northing)
        northingLen = len(northingStr)
        if northingLen > 14:
            northingLen = 14

        return eastingStr[:eastingLen] + ',' + northingStr[:northingLen]

    def getOSGridRef(self, no_figures):
        eastingStr = '{0:0>6}'.format(int(self.easting))
        northingStr = '{0:0>7}'.format(int(self.northing))

        osLetters = self.getOSLetters(int(eastingStr[:1]),int(northingStr[:2]))

        if osLetters != 'Unknown':
            return osLetters + eastingStr[1:no_figures] + northingStr[2:no_figures]
        return eastingStr.strip("0") + ',' + northingStr.strip("0")

    def getOSLetters(self, x, y):
        if y == 0:
            if x == 0:
                return 'SV'
            if x == 1:
                return 'SW'
            if x == 2:
                return 'SX'
            if x == 3:
                return 'SY'
            if x == 4:
                return 'SZ'
            if x == 5:
                return 'TV'
            return 'Unknown'
        if y == 1:
            if x == 1:
                return 'SR'
            if x == 2:
                return 'SS'
            if x == 3:
                return 'ST'
            if x == 4:
                return 'SU'
            if x == 5:
                return 'TQ'
            if x ==6:
                return 'TR'
            return 'Unknown'
        if y == 2:
            if x == 1:
                return 'SM'
            if x == 2:
                return 'SN'
            if x == 3:
                return 'SO'
            if x == 4:
                return 'SP'
            if x == 5:
                return 'TL'
            if x ==6:
                return 'TM'
            return 'Unknown'
        if y == 3:
            if x == 2:
                return 'SH'
            if x == 3:
                return 'SJ'
            if x == 4:
                return 'SK'
            if x == 5:
                return 'TF'
            if x ==6:
                return 'TG'
            return 'Unknown'
        if y == 4:
            if x == 2:
                return 'SC'
            if x == 3:
                return 'SD'
            if x == 4:
                return 'SE'
            if x == 5:
                return 'TA'
            return 'Unknown'
        if y == 5:
            if x == 1:
                return 'NW'
            if x == 2:
                return 'NX'
            if x == 3:
                return 'NY'
            if x == 4:
                return 'NZ'
            if x == 5:
                return 'OV'
            return 'Unknown'
        if y == 6:
            if x == 1:
                return 'NR'
            if x == 2:
                return 'NS'
            if x == 3:
                return 'NT'
            if x == 4:
                return 'NU'
            return 'Unknown'
        if y == 7:
            if x == 0:
                return 'NL'
            if x == 1:
                return 'NM'
            if x == 2:
                return 'NN'
            if x == 3:
                return 'NO'
            if x == 4:
                return 'NP'
            return 'Unknown'
        if y == 8:
            if x == 0:
                return 'NF'
            if x == 1:
                return 'NG'
            if x == 2:
                return 'NH'
            if x == 3:
                return 'NJ'
            if x == 4:
                return 'NK'
            return 'Unknown'
        if y == 9:
            if x == 0:
                return 'NA'
            if x == 1:
                return 'NB'
            if x == 2:
                return 'NC'
            if x == 3:
                return 'ND'
            if x == 4:
                return 'NE'
            return 'Unknown'
        if y == 10:
            if x == 1:
                return 'HW'
            if x == 2:
                return 'HX'
            if x == 3:
                return 'HY'
            if x == 4:
                return 'HZ'
            return 'Unknown'
        if y == 11:
            if x == 3:
                return 'HT'
            if x == 4:
                return 'HU'
            return 'Unknown'
        if y == 12:
            if x == 3:
                return 'HO'
            if x == 4:
                return 'HP'
            return 'Unknown'
        return 'Unknown'
            