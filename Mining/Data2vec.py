import os
import numpy
#import pandas as pd
import csv
import copy

def is_japanese(string):
    for s in string:
        name = unicodedata.name(s)
        print(name)
        if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return True
    return False

filepath = 'dat/水質・底質/'
#rivername = '粟津沖中央'
submode = '任意期間水質'

files = os.listdir(filepath)
outputfiles = os.listdir("tmp/")
Ecoilindex = 61 + 3
rivername = []

for file in files:
    if not file.split("_")[0] in rivername and submode in file and not file.split("_")[0] + ".csv" in outputfiles:
        rivername.append(file.split("_")[0])

for river in rivername:
    print(river)
    datas = []
    for file in files:
        if river + "_" + submode in file:
            print(file)
            #df = pd.read_csv(filepath + file,sep = ',')
            f = open(filepath + file,'r')
            reader = csv.reader(f)
            header = next(reader)
            titleflag = False
            i = 0
            for row in reader:
                #print(row)
                if row:
                    if row[0] == "類型":
                        titleflag = True
                        i = 0
                    if titleflag == True and i ==2:
                        titlerow = row
                        titleflag = False
                        i = 0
                    if titleflag == True:
                        i += 1
                    if row[0].replace('/','').isdigit():
                        diffsize = len(titlerow) - (len(row)-3)
                        datas.append([copy.copy(titlerow),row + [" " for n in range(diffsize)]])
                        #print(titlerow,row)
                        #input()
            #if "糞便性大腸菌群数" in data:
            #titlerow = []
            f.close()
    #print(datas)
    Ecoil = []
    date = []
    time = []
    place = []
    for data in datas:
        if "糞便性大腸菌群数" in data[0] and data[1][Ecoilindex] != " ":
            Ecoil.append(data)
            date.append(data[1][0])
            time.append(data[1][1])
            place.append(data[1][2])
            datas.remove(data)
            #print(data)
            #input()

    #print(date,time,place)
    #pulleddata = copy.copy(Ecoil)
    for data in datas:
        if data[1][0] in date and data[1][1] in time and data[1][2] in place:
            for ecoil in Ecoil:
                if data[1][0] in ecoil[1] and data[1][1] in ecoil[1] and data[1][2] in ecoil[1]:
                #if data[1][0] in ecoil[1]:
                #    if data[1][1] in ecoil[1]:
                #        if data[1][2] in ecoil[1]:''
                    #print(i)
                    #if not data[0][0] in ecoil[0]:
                    ecoil[0] += data[0]
                    ecoil[1] += data[1][3:]
                    #print(ecoil[1],data[1][0],data[1][1],data[1][2])
                    #print(data[1])
                    #print(ecoil[0])
                    #print(ecoil[1])
                    #input()
                    #pulleddata.append([ecoil[0] + data[0],ecoil[1] + data[1][3:]])


    #print(Ecoil)
    removeindex = []
    for ecoil in Ecoil:
        tmp = []
        for i in range(len(ecoil[1])):
            if ecoil[1][i] == " ":
                tmp.append(i)
        removeindex.append(tmp)
        #print(removeindex)
        #input()
    for ecoil in Ecoil:
        for i in reversed(removeindex[Ecoil.index(ecoil)]):
            #print(ecoil[0])
            ecoil[0].pop(i-3)
            ecoil[1].pop(i)
        #print(ecoil)
        #input()

    f = open("tmp/" + river + ".csv","w")

    writer = csv.writer(f)
    for tmp in Ecoil:
        writer.writerow([0,0,0] + tmp[0])
        writer.writerow(tmp[1])

    f.close()
    #input()
