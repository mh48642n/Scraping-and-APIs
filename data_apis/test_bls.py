import datetime 
import json
import pandas as pd
import requests as rq

class BLS:

    def __init__(self, key):

        # header needed for json collection process
        self.header = {'Content-type' : 'application/json'}

        # API key pointed to when the class object is created
        self.key = key

    def macro_data(self, json_object = None):

        # assesses if it is actually a json object to begin pulling process
        if(json_object != None):

            # iterates over parameters in json object to find the data needed
            # assigns dataframes to a particular table name that will fit into the database
            return {k: self.build_url(json_object[k]) for k in json_object.keys()}
        
    
    def build_url(self, object):

        # checks the distance between years
        if((object[2] - object[1]) <= 20):

            #
            return self.format_json(object[1], object[2], object[3])

        else:

            years = self.struct_time((object[2] - object[1]))

            for year in years:

                                   

    def format_json(self, begin, end, series):

        dumps = json.dumps({"seriesid" : series, 
                            "startyear": begin, "endyear" : end, 
                            "registrationkey": self.key})
        res = rq.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data = data, headers = {"Content-type" : "application/json"})
        data = json.loads(res.text)


        if(data != None):
            for v in range(0, len(data)):
                box = pd.DataFrame(data[v]['data']).rename(columns = {"value" : data[v]['seriesID']})
                data = self.struct_time(box)
                stuff = stuff[["dates", data[v]['seriesID']]]

                if v == 0:
                    first = stuff
                else:
                    first = pd.merge(first, stuff)

            return first.sort_values(by = "dates").reset_index(drop = True)


    
    def struct_time(self, spread):

        

        return  
