import json
import dml
import prov.model
import datetime
import pandas as pd
from bson.son import SON
import uuid
import scipy.stats

class correlation_propval_crime(dml.Algorithm):
    contributor = 'alsk_yinghang'
    reads = ['alsk_yinghang.crime_properties']
    writes = ['alsk_yinghang.prop_val_crimes']

    @staticmethod
    def execute(trial=False):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('alsk_yinghang', 'alsk_yinghang')
        n = 0
        propval_crime = {}
        for doc in repo['alsk_yinghang.crime_properties'].find():
            if n > 10000 and trial:
              break
            avg_prop_val = int(round(doc['avg_prop_val'], -6))
            if avg_prop_val not in propval_crime.keys():
                propval_crime[avg_prop_val] = 1
            else:
                propval_crime[avg_prop_val] += 1
            n+=1
        
        temp = []
        for avg_prop_val in propval_crime.keys():
            num_crimes = propval_crime[avg_prop_val]
            temp.append({'avg_prop_val': avg_prop_val, 'num_of_crimes': num_crimes})

        repo.dropPermanent("prop_val_crimes")
        repo.createPermanent("prop_val_crimes")
        repo['alsk_yinghang.prop_val_crimes'].insert_many(temp)

        print('Determining correlation.....')
        data = [(avg_prop_val, propval_crime[avg_prop_val]) for avg_prop_val in propval_crime.keys()]
        avg_prop_val = [x for (x, y) in data]
        num_crimes = [y for (x, y) in data]

        result = scipy.stats.pearsonr(avg_prop_val, num_crimes)

        correlation_cofficient = result[0]

        pvalue = result[1]

        print('The correlation coefficient is: ' + str(correlation_cofficient) + '.')
        if correlation_cofficient < 0:
            print('There is a negative correlation between the average property value and the number of crimes.')
        elif correlation_cofficient > 0:
            print('There is a positive correlation between the average property value and the number of crimes.')
        else:
            print('This tells us that there does not appear to be any correlation between the average property value and the number of crimes.')
        print('The p-value obtained is: ' + str(pvalue) + '.')
        if pvalue < 0.01:
            print("The result is statistically highly significant ")
        if pvalue < 0.05 and pvalue > 0.01:
            print("The result is statistically significant ")

        print('According to scipy online documentation, "The p-value roughly indicates the probability of an uncorrelated system producing datasets that have a Pearson correlation at least as extreme as the one computed from these datasets. "')

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        return

correlation_propval_crime.execute()
