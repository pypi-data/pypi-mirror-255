#!/usr/bin/env python3

import json
from pathlib import Path


import boto3
import datetime
from dateutil.relativedelta import relativedelta

today = datetime.datetime.today()
year = datetime.datetime.now().year
day = datetime.datetime.now().day
month = datetime.datetime.now().month
end1 = datetime.datetime(year,month,1)+ relativedelta(months=1, days=-1)
start2 = datetime.datetime(year,month,day)
end2 = datetime.datetime(year,month,day)+ relativedelta(months=1, days=-1)
start1 = end1 + relativedelta(months=-2, days=1)
start = start1.strftime('%Y-%m-%d')
startC = start2.strftime('%Y-%m-%d')
endC = end2.strftime('%Y-%m-%d')
s=datetime.datetime(year,month,1)

sC = s.strftime('%Y-%m-%d')
cd = boto3.client('ce')

results = []
results1 = []
response1 = []
print('boto3 version')
print(boto3.__version__)
token = None
while True:
    if token:
        kwargs = {'NextPageToken': token}
    else:
        kwargs = {}

    data2 = cd.get_cost_forecast(TimePeriod={'Start': startC, 'End':  endC}, Granularity='MONTHLY', Metric="UNBLENDED_COST", **kwargs)
    results += data2['ForecastResultsByTime']
    token = data2.get('NextPageToken')
    if not token:
        break
token1 = None
while True:
    if token1:
        kwargs = {'NextPageToken': token}
    else:
        kwargs = {}
    data1 = cd.get_cost_and_usage(TimePeriod={ 'Start': sC, 'End': startC}, Granularity='MONTHLY', Metrics=['UnblendedCost'], **kwargs)
    results1 += data1['ResultsByTime']
    token1 = data1.get('NextPageToken')
    if not token1:
        break
response = cd.get_cost_and_usage(
    TimePeriod={
        'Start': sC,
        'End': startC
    },
    Granularity='MONTHLY',
    Metrics=[
        'BlendedCost'
    ],GroupBy=[
        {
            'Type': 'DIMENSION',
            'Key': 'SERVICE'
        }, ]
)
response1 += response['ResultsByTime']
#dans json
now = datetime.datetime.now()
date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
dictionary ={
    "today": date_time,
    "total": results1[0],
    "Couts": response1[0],
    "prevus" : results[0],

}
path = Path("reports")
path.mkdir(parents=True, exist_ok=True)
with open('reports/cost.json','w',newline='') as f:  #Ouverture du fichier CSV en écriture
    print("file cost json created")
    json.dump(dictionary,f)               # Mettre dans la variable ecrire cette nouvelle ligne


