import datetime 
import json
import pandas as pd
import requests as rqs
import math

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
        if((object[1] - object[0]) <= 20):

            # returns a dictionary filled with columns to a particular key
            return self.format_json(object[0], object[1], object[2])

        else:

            # gets a list of years from the struct_time method based on the spread of the years 
            years = self.struct_time((object[1] - object[0]), object[0], object[1])

            # creates an empty dataframe
            start = pd.DataFrame()

            # pull data from bls in time periods less than equal to 20 
            for year in years:

                # takes the time period and pulls data from that time period
                end = self.format_json(year[0], year[1], object[2])

                # adds the dataframe end to this dataframe called start through concatenation 
                start = pd.concat([start, end], axis = 1)

            # gets rid of any duplicates
            start = start.drop_duplicates(["year", "period", "periodName"])
            return start
                                   

    def format_json(self, begin, end, series):

        # formula for pulling data from BLS API
        dumps = json.dumps({"seriesid" : [series], 
                            "startyear": begin, "endyear" : end, 
                            "registrationkey": self.key})
        res = rqs.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data = dumps, headers = {"Content-type" : "application/json"})
        data = json.loads(res.text)["Results"]["series"][0]

        # making sure that data exists
        try:

            # converts list of dictionaryies into a pandas dataframe
            info = pd.DataFrame(data["data"]).rename(columns = {"value" : data["seriesID"]})

        except KeyError:
            print("Data not found or program malfunction")   

        return info.sort_values(by = ["year", "period"]).reset_index(drop = True)


    
    def struct_time(self, time, begin, end):

        # focuses on finding the optimal sectioning for the years given the spread
        i = 2
        while True:
            section = math.floor((end - begin) / i)

            if ((section >= 10) & (section <= 20.0)):
                break

            i += 1

        # focuses on adding to a list the years sectioned given the optimal sectioning
        times = []
        for b in range(0, i + 2):

            if b == 0:
                times.append((begin, begin + section))

            elif times[b - 1][1] == end:
                break

            elif (end - times[b - 1][1]) < section: 
                    times.append((times[b - 1][1], end))

            elif b != i:
                times.append((times[b - 1][1], times[b - 1][1] + section))

        return times
    
