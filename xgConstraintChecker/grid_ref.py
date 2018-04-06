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
        else:
            return eastingStr.strip("0") + ',' + northingStr.strip("0")
        
    def getOSLetters(self, x, y):
        if y == 0:
            if x == 0:
                return 'SV'
            elif x == 1:
                return 'SW'
            elif x == 2:
                return 'SX'
            elif x == 3:
                return 'SY'
            elif x == 4:
                return 'SZ'
            elif x == 5:
                return 'TV'
            else:
                return 'Unknown'
        elif y == 1:
            if x == 1:
                return 'SR'
            elif x == 2:
                return 'SS'
            elif x == 3:
                return 'ST'
            elif x == 4:
                return 'SU'
            elif x == 5:
                return 'TQ'
            elif x ==6:
                return 'TR'
            else:
                return 'Unknown'
        elif y == 2:
            if x == 1:
                return 'SM'
            elif x == 2:
                return 'SN'
            elif x == 3:
                return 'SO'
            elif x == 4:
                return 'SP'
            elif x == 5:
                return 'TL'
            elif x ==6:
                return 'TM'
            else:
                return 'Unknown'
        elif y == 3:
            if x == 2:
                return 'SH'
            elif x == 3:
                return 'SJ'
            elif x == 4:
                return 'SK'
            elif x == 5:
                return 'TF'
            elif x ==6:
                return 'TG'
            else:
                return 'Unknown'
        elif y == 4:
            if x == 2:
                return 'SC'
            elif x == 3:
                return 'SD'
            elif x == 4:
                return 'SE'
            elif x == 5:
                return 'TA'
            else:
                return 'Unknown'
        elif y == 5:
            if x == 1:
                return 'NW'
            elif x == 2:
                return 'NX'
            elif x == 3:
                return 'NY'
            elif x == 4:
                return 'NZ'
            elif x == 5:
                return 'OV'
            else:
                return 'Unknown'
        elif y == 6:
            if x == 1:
                return 'NR'
            elif x == 2:
                return 'NS'
            elif x == 3:
                return 'NT'
            elif x == 4:
                return 'NU'
            else:
                return 'Unknown'
        elif y == 7:
            if x == 0:
                return 'NL'
            elif x == 1:
                return 'NM'
            elif x == 2:
                return 'NN'
            elif x == 3:
                return 'NO'
            elif x == 4:
                return 'NP'
            else:
                return 'Unknown'
        elif y == 8:
            if x == 0:
                return 'NF'
            elif x == 1:
                return 'NG'
            elif x == 2:
                return 'NH'
            elif x == 3:
                return 'NJ'
            elif x == 4:
                return 'NK'
            else:
                return 'Unknown'
        elif y == 9:
            if x == 0:
                return 'NA'
            elif x == 1:
                return 'NB'
            elif x == 2:
                return 'NC'
            elif x == 3:
                return 'ND'
            elif x == 4:
                return 'NE'
            else:
                return 'Unknown'
        elif y == 10:
            if x == 1:
                return 'HW'
            elif x == 2:
                return 'HX'
            elif x == 3:
                return 'HY'
            elif x == 4:
                return 'HZ'
            else:
                return 'Unknown'
        elif y == 11:
            if x == 3:
                return 'HT'
            elif x == 4:
                return 'HU'
            else:
                return 'Unknown'
        elif y == 12:
            if x == 3:
                return 'HO'
            elif x == 4:
                return 'HP'
            else:
                return 'Unknown'
        else:
            return 'Unknown'
        
            