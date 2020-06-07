# -*- coding: utf-8 -*-
"""
Created on Sun May 24 22:37:36 2020

@author: travm
"""


import pandas as pd
import os

#Move to the directory
#os.chdir('C:/Users/travm/Desktop/FantasyFootball_Analysis') #Desktop
os.chdir('/users/admin/blog_data/FantasyFootball2020/FantasyFootball')
#Open the file
NFL2019playbyplay = pd.read_csv('2019playBYplay.csv')

#Determine Change in possesion
#Step sort by game id and time
NFL2019pbp_gamesort = NFL2019playbyplay.sort_values(by=['GameId','Quarter','Minute','Second'],ascending=[True,True,False,False] ).reset_index().drop(columns='index')
#Step 2 create a new column shifted 1 down
NFL2019pbp_gamesort['offenseShift'] = NFL2019pbp_gamesort['OffenseTeam'].shift(-1)
columnSort = NFL2019pbp_gamesort.columns.tolist()
columnSort2 = columnSort[:6] + [columnSort[-1]] + columnSort[6:-2]

NFL2019pbp_gamesort = NFL2019pbp_gamesort[columnSort2]
#Define the change of possesion function
def changePoss(offTeam,offshiftTeam):
    if offTeam == offshiftTeam:
        return 0
    elif offTeam != offshiftTeam:
        return 1
    
NFL2019pbp_gamesort['changeINpossesion'] = NFL2019pbp_gamesort.apply(lambda x: changePoss(x.OffenseTeam,x.offenseShift),axis=1)


#Parse out the qb's
#Step 1. Get the complete list of nfl QB's
qb2019 = pd.read_csv('qb2019total.csv')
qb2019['Player'] = qb2019['Player'].apply(lambda x: x.replace('*','').replace('+',''))
qb2019['LastName']= qb2019['Player'].apply(lambda x: x.split(' ',1)[1].upper())
qb2019['FirstInitial'] = qb2019['Player'].apply(lambda x: x[0])
qb2019['descName'] = qb2019.apply(lambda x: x.FirstInitial + '.' + x.LastName,axis=1)


#Create list of names
qb2019List = list(qb2019['descName'])

#Filter the QB data
columnList = []
columnListQB = []
for qb in qb2019List:
    NFL2019pbp_gamesort['QBattr'+qb]=NFL2019pbp_gamesort['Description'].apply(lambda x: 1 if qb in x[:47] else 0 )
    NFL2019pbp_gamesort['QBname '+qb]=NFL2019pbp_gamesort['Description'].apply(lambda x: qb if qb in x[:47] else '')
    columnList.append('QBattr'+qb)
    columnListQB.append('QBname '+qb)
#Now sum the rows from 
NFL2019pbp_gamesort['QBsumattr'] = NFL2019pbp_gamesort[columnList].sum(axis=1)
NFL2019pbp_gamesort['QBnames']   = NFL2019pbp_gamesort[columnListQB].sum(axis=1)
NFL2019pbp = NFL2019pbp_gamesort.drop(columns=columnList+columnListQB)

#Now filter for rows with 1:
NFL2019pbpQB = NFL2019pbp[(NFL2019pbp['QBsumattr'] == 1) | (NFL2019pbp['QBsumattr'] == 2)]
NFL2019pbpQB_1 = NFL2019pbp[(NFL2019pbp['QBsumattr'] == 1)]
NFL2019pbpQB_2 = NFL2019pbp[(NFL2019pbp['QBsumattr'] == 2)]




#Ok now we have the qb data
#Order by game id and qb
NFL2019pbpQBsorted = NFL2019pbpQB.sort_values(by=['GameId','QBnames','Quarter','Minute','Second'])



    

def pointsPerPlay(playType,tdCol,intCol,yardCol,fumbCol,possesionCol):
    #Step 1 determine if pass,rush or scramble
    
    #Passing Situation only 3 scenarios Complete, TD, Interception
    #Incomplete, Sack, Fumble do not detract from QB's points
    if playType == 'PASS':
        if (tdCol == 1 and intCol == 0):
            return yardCol/25.0 + 4.0
        elif (tdCol == 0 and intCol == 0):
            return yardCol/25.0
        elif intCol == 1:
            return -1.0
    elif playType == 'RUSH' or playType =='SCRAMBLE' or playType =='QB KNEEL':
        if fumbCol == 1 and possesionCol == 1:
            return yardCol/10.0 - 2.0
        elif fumbCol ==1 and possesionCol == 0:
            return yardCol/10.0 - 1.0
        else:
            if tdCol == 1:
                return yardCol/10.0 + 6.0
            elif tdCol == 0:
                return yardCol/10.0
    elif playType == 'FUMBLES' and possesionCol == 1:
        return yardCol/10.0 - 2.0
    elif playType == 'FUMBLES' and possesionCol == 0:
        return yardCol/10.0 - 1.0
        

    
NFL2019pbpQBsorted['FntsyPts_Play'] = NFL2019pbpQBsorted.apply(lambda x: pointsPerPlay(x.PlayType,x.IsTouchdown,x.IsInterception,x.Yards,x.IsFumble,x.changeINpossesion),axis=1)


NFL2019pbpQBsorted.to_csv('FntsyQBanalysis.csv')

import matplotlib.pyplot as plt
import seaborn as sns

%matplotlib qt

#By game by QB
aRodgers2019 = NFL2019pbpQBsorted[NFL2019pbpQBsorted.QBnames == 'A.RODGERS']

sns.boxplot(y='FntsyPts_Play',x='GameId'
            ,data = aRodgers2019,
            palette = 'colorblind',
            hue='GameId')
plt.show()

bplot1 = sns.stripplot(y='FntsyPts_Play',x='GameId',
                       data = aRodgers2019,
                       jitter = True,
                       marker = 'o',
                       alpha = 0.5,
                       dodge = True,
                       hue = 'Formation')



