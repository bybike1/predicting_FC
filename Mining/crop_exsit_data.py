import os
import csv
from time import sleep
from matplotlib import pyplot
import datetime
import copy
import time
import numpy as np
from statistics import mean,stdev

def daterange(start, stop, term):
    for n in range(0, int((stop - start).day),30*term):
        yield start.month + datetime.deltad

class Data():
    def __init__(self,date,time,place,title,datas):
        self.date = date
        self.time = time
        self.place = place
        self.title = title
        self.datas = datas
class Point():
    def __init__(self,point):
        self.point = point
        self.datas = []
        self.vector = []

    def append_data(self,data):
        self.datas.append(data)

    def merge_samedate(self):
        tmp = []
        for data in self.datas:
            tmp.append(data.date)

        for i, data in enumerate(self.datas):
            if data.date in tmp[i+1:]:
                sameindex = tmp[i+1:].index(data.date) + i + 1
                tmpdatas = self.datas[sameindex].datas
                hoge = []
                for j, d in enumerate(tmpdatas):
                    #print("a:" +str(data.datas[j]))
                    #print("b:" +str(self.datas[sameindex].datas[j]))
                    #print(data.date)
                    #print(self.datas[sameindex].date)
                    hoge.append((d + data.datas[j])/2.0)
                self.datas[sameindex].datas = hoge
                #print(hoge)
                tmp.pop(self.datas.index(data))
                self.datas.remove(data)

    def merge_samemonth(self):
        tmp = []
        for data in self.datas:
            tmp.append(data.date)

        for i, data in enumerate(self.datas):
            if data.date in tmp[i+1:]:
                sameindex = tmp[i+1:].index(data.date) + i + 1
                tmpdatas = self.datas[sameindex].datas
                hoge = []
                for j, d in enumerate(tmpdatas):
                    #print("a:" +str(data.datas[j]))
                    #print("b:" +str(self.datas[sameindex].datas[j]))
                    #print(data.date)
                    #print(self.datas[sameindex].date)
                    hoge.append((d + data.datas[j])/2.0)
                self.datas[sameindex].datas = hoge
                #print(hoge)
                tmp.pop(self.datas.index(data))
                self.datas.remove(data)

    def createVec(self,term):
        hogedate = []
        #print(self.point)
        for data in self.datas:
            #print(data.date)
            hogedate.append(data.time)
        mindate = min(hogedate)
        maxdate = max(hogedate)
        #print(mindate)
        #print(maxdate)
        termmonth = mindate
        if termmonth.month % 2 == 0:
            termmonth = datetime.datetime.fromtimestamp(time.mktime((termmonth.year,termmonth.month-1,1,0,0,0,0,0,0)))
        else:
            termmonth = datetime.datetime.fromtimestamp(time.mktime((termmonth.year,termmonth.month,1,0,0,0,0,0,0)))
        while True:
            #print(termmonth)
            if (termmonth.year == maxdate.year and termmonth.month >= maxdate.month) or termmonth.year > maxdate.year:
                break
            tmp = []
            for i, date in enumerate(hogedate):
                if termmonth <= date < datetime.datetime.fromtimestamp(time.mktime((termmonth.year,termmonth.month+term,1,0,0,0,0,0,0))):
                    print(date)
                    print(self.datas[i].date)
                    tmp.append(self.datas[i])
            hoge = []
            ave = []
            if tmp:
                for i in range(len(tmp[0].datas)):
                    tenti = []
                    for j in range(len(tmp)):
                        tenti.append(tmp[j].datas[i])
                    ave.append(sum(tenti)/len(tenti))
                self.vector.append([termmonth,ave])
            else:
                self.vector.append([termmonth,None])
            termmonth = datetime.datetime.fromtimestamp(time.mktime((termmonth.year,termmonth.month+term,1,0,0,0,0,0,0)))
            #print(self.vector)
        tmp = []
        for vec in self.vector:
            if vec[1] != None:
                tmp.append(1)
            else:
                tmp.append(0)
        #print(tmp)
        exist = [0 for i in range(len(tmp))]
        for i in range(len(tmp)-11):
            piyo = 0
            for j in range(12):
                piyo = piyo + tmp[i + j]
            if piyo == 12:
                for hoge in range(i, i + 12):
                    exist[hoge] = 1
            #print(piyo)
        #print(tmp)
        #print(exist)
        tmp = []
        for i,vec in enumerate(self.vector):
            if exist[i] == 1:
                tmp.append(vec)
        self.vector = tmp
        #print(self.vector)
    def normalize(self):
        m = []
        l = []
        if self.vector:
            tmp = []
            for i in range(len(self.vector[0][1])):
                tenti = []
                for j in range(len(self.vector)):
                    tenti.append(self.vector[j][1][i])
                m.append(max(tenti))
                l.append(min(tenti))
                for j in range(len(self.vector)):
                    #if i != 0:
                    if m[i] - l[i] != 0.0:
                        self.vector[j][1][i] = (tenti[j] - l[i])/(m[i] - l[i])
                    else:
                        self.vector[j][1][i] = 0
                    #print(tenti[j]/m[i])
            #self.vector[1] = copy.copy(tmp)
            #print(self.vector)
        #self.vec
    def regularize(self):
        m = []
        s = []
        if self.vector:
            tmp = []
            for i in range(len(self.vector[0][1])):
                tenti = []
                for j in range(len(self.vector)):
                    print(self.vector[j][1][i])
                    tenti.append(self.vector[j][1][i])
                m.append(mean(tenti))
                s.append(stdev(tenti))
                for j in range(len(self.vector)):
                    print(self.point)
                    print(s[i])
                    #if i != 0:
                    if s[i] != 0.0:
                        self.vector[j][1][i] = (tenti[j] - m[i])/(s[i])
                    else:
                        self.vector[j][1][i] = 0
                    #print(tenti[j]/m[i])
            #self.vector[1] = copy.copy(tmp)


path = "./tmp/"
points = []
files = os.listdir(path)
for file in files:
    f = open(path + file,"r")
    reader = csv.reader(f)
    try:
        #header = next(reader)
        points.append(Point(file.strip(".csv")))
        #print(points[-1].point)
        title = []
        for row in reader:
            if row:
                if row[0] == '0':
                    title = row[3:]
                    #print(title)
                else:
                    points[-1].append_data(Data(datetime.date(int(row[0].split('/')[0]),int(row[0].split('/')[1]),int(row[0].split('/')[2])),
                    datetime.datetime(int(row[0].split('/')[0]),int(row[0].split('/')[1]),int(row[0].split('/')[2]),int(row[1].replace(".",":").replace("24","0").split(':')[0]),int(row[1].replace(".",":").split(':')[1])),
                    row[2],title,row[3:]))
                    #print(points[-1].datas[-1].title)
                    #sleep(10)
    except StopIteration:
        print("None")
#for point in points:
#    print(len(point.datas))
hasi = points[0]
unko = []
tisso = []
ph = []
bod = []
ss = []
do = []
cod = []
existpoints = []
for p in points:
    existpoints.append(Point(p.point))
    for data in p.datas:
        existflag = False
        unko.append(data.datas[data.title.index("糞便性大腸菌群数")])
        #if '総窒素' in data.title:
        #    tisso.append(data.datas[data.title.index("総窒素")])
        #else:
        if not '導電率' in data.title:
            existflag = True
        #    tisso.append(None)
        if not '#ｐＨ' in data.title:
            existflag = True
        if not 'ＢＯＤ' in data.title:
            existflag = True
#            bod.append(data.datas[data.title.index("ＢＯＤ")].replace("<",""))
#            if float(bod[-1]) < 0.5:
#                bod[-1] = str(0.5)
        if not 'ＳＳ' in data.title:
            existflag = True
        if not 'ＤＯ' in data.title:
            existflag = True
        if not '気温' in data.title:
            existflag = True
        if not '水温' in data.title:
            existflag = True
        if existflag == False:
            existpoints[-1].append_data(data)
    #    if 'ＣＯＤ' in data.title:
    #        cod.append(data.datas[data.title.index("ＣＯＤ")])
    #    else:
    #        cod.append(None)
croppoints = []
for point in existpoints:
    tmpdata = []
    croppoints.append(Point(point.point))
    for data in point.datas:
        tmpdata =[data.datas[data.title.index("糞便性大腸菌群数")],
            data.datas[data.title.index("導電率")],
            data.datas[data.title.index("#ｐＨ")],
            data.datas[data.title.index("ＢＯＤ")],
            data.datas[data.title.index("ＳＳ")],
            data.datas[data.title.index("ＤＯ")],
            data.datas[data.title.index("気温")],
            data.datas[data.title.index("水温")]]
        strflag = False
        for i, tmp in enumerate(tmpdata):
            #print(tmp)
            if tmp.strip(">").strip("<").replace(".","").strip("-").replace("+","").replace("E","").isdigit():
                tmpdata[i] = float(tmp.strip(">").strip("<"))
                #print(tmpdata[i])
            else:
                strflag = True
                break
        if strflag == False:
            tmpdata = Data(data.date,data.time,data.place,["糞便性大腸菌群数","導電率","#ｐＨ","ＢＯＤ","ＳＳ","ＤＯ","気温","水温"],tmpdata)
            croppoints[-1].append_data(tmpdata)
    if len(croppoints[-1].datas) == 0:
        croppoints.pop()
        #print(croppoints[-1].datas[-1].datas)

for point in croppoints:
    print(point.point)
    point.merge_samedate()
#    for data in point.datas:
#        print(data.date)
#for point in croppoints:
#    for data in point.datas:
#        print(data.date)
unko = []
for point in croppoints:
    point.createVec(2)
    for data in point.vector:
        unko.append(data[1][0])
    #point.regularize()
    #point.normalize()
#hoge = [data[:][1][:] for data in croppoints[-1].vector]
#array = np.array(hoge[:][2])
"""
for point in croppoints:
    tmp = []
    for data in point.datas:
        tmp.append(data.date)
        #print(data.datas)
    for i, data in enumerate(point.datas):
        if data.date in tmp[:i] + tmp[i+1:]:# and not (point.datas.index(data) == tmp.index(data.date)):
            point.datas = point.datas[reversed(tmp).index(data.date)] +
"""
f = open('datas.csv','w')

writer = csv.writer(f)
for point in croppoints:
    for vec in point.vector:
        print(vec[1][0])
        writer.writerow(vec[1])

f.close()
#p1 = pyplot.plot(normalize(array), label = "kuso")
#p2 = pyplot.plot(tisso,label = "tisso")
#p3 = pyplot.plot(ph,label = "ph")
#p4 = pyplot.plot(bod,label = "bod")
#p5 = pyplot.plot(ss,label = "ss")
#p6 = pyplot.plot(do,label = "do")
#p7 = pyplot.plot(cod,label = "cod")
#pyplot.legend()
#pyplot.legend([p1,p2,p3,p4,p5,p6],["糞便性","窒素","ph","bod","ss","do"])
#pyplot.show()
"""
existtitle = points[0].datas[0].title
for point in points:
    for data in point.datas:
        existtitle = list(set(existtitle) & set(data.title))
        #print(existtitle)
        #sleep(1)
print(existtitle)
"""
