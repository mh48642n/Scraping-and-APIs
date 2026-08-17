import pandas as pd
import requests as rq

header = {
    "User-Agent" : "Student Mars"
}

class BEA:

    def __init__(self, key):
        self.url = "http://apps.bea.gov/api/data?&UserID=" + key

    def data_pull(self, pull_this, *json_table):

        match(pull_this):     

            # pull survey names
            case 1:

                pulled = self.format_json("&method=GETDATASETLIST&ResultFormat=JSON", pull_this)

                for i in range(0, len(pulled)):
                    print(pulled[i]["DatasetName"] + " - " + pulled[i]["DatasetDescription"])

            # pulls tables names in a survey and their table codes
            case 2:

                pulled = self.format_json(self.url + "&method=GetParameterValues&datasetname=" + input("What survey?.....") + 
                                "&ParameterName=TableName&ResultFormat=JSON")

                confirm = "True"

                # prompting user to input 
                while confirm == "True":    
                    
                    range_vals = input("Input a range of values as XXX-XXX(59-150, 1-10): ").split("-")

                    for i in range(int(range_vals[0]), int(range_vals[1])):
                        print(pulled["TableName"][i], "....", pulled["TableDescription"][i])

                    confirm = input("\n\nDo you want to look at more tables(True or False):")

            # pulls table 
            case 3:  
                self.macro_data(json_table)


    def macro_data(self, json_object, year = "All", tables = None):
        
        # Pulling all tables for the first time
        if(year == "All" and tables == None):

            # iterates over parameters in json object to find the data needed
            # assigns dataframes to a particular table name that will fit into the database
            return {k : self.build_url(json_object[k], year) for k in json_object.keys()}

        # Adding data to already existing tables or pulling data for quick use         
        elif(year != "All" | tables != None):

            # iterates over parameters in json object to find the data needed
            # assigns dataframes to a particular table name that will fit into the database
            return {k : self.build_url(json_object[k], year) for k in tables}
                      
                
    def build_url(self, parameters, year):

        # checks if this a list of parameters instead of just a string
        # if it is a string it skips to the return statement outside of the function
        if isinstance(parameters, list):
            print(parameters[2])
            # this puts the parameters into the parts of the url
            url = "&method=GetData&DataSetName=" + parameters[0] + "&TableName=" + parameters[2] + "&tableID=ALL&Frequency=" + parameters[1] + "&Year=" + year + "&ResultFormat=JSON"

            # returns the results of the json pull with the specific parameters included 
            return self.format_json(url)

        # returns json pull given the specific url string
        return self.format_json(parameters)
        

    def format_json(self, url_end, *select):
        
        # makes the full url for the pull
        total_url = self.url + url_end
        
        # extracts the data from the API
        pull = rq.get(total_url, headers = header)

        # returns json file for surveys 
        if(select == 1):
            return pull.json()["BEAAPI"]["Results"]["Data"]

        # returns json file for list of tables to search through 
        if(select == 2):
            return pull.json()["BEAAPI"]["Results"]["ParamValue"]
            
        # FOR TABLE EXTRACTS 
        # takes the note if it is there
        try:
            note = pull.json()["BEAAPI"]["Results"]["Notes"][0]['NoteText']
        except KeyError:
            print("No notes for Table ", pull.json()["BEAAPI"]["Results"]["Dataset"][0].get("TableName"),
                ", the type of table is a ", pull.json()["BEAAPI"]["Results"]["Dataset"].get("Statistic"))

        # converts the API into json then into a dataframe getting a table
        data = pd.DataFrame(pull.json()["BEAAPI"]["Results"]["Data"])

  

        return self.format_data(data, note)
    
        
    def format_data(self, table, note = None):
        
        # subsets the data by economic account
        description = table["LineDescription"].unique()
        
        # creates an empty dataframe
        concat = pd.DataFrame()        

        # takes the list of economic accounts and iterates with it
        for item in description:

            # creates a dataframe with that economic account name column, data value and date
            df = table[table["LineDescription"] == item]

            # pivots that dataframe around the date, with the focus of creating a column
            # with the economic account's name and it the associated data value with the date
            # it is made for
            df = df.pivot_table(index = "TimePeriod", columns = "LineDescription", values = "DataValue", aggfunc = 'first')
            
            # concats the new column into the empty dataframe and then adds on each new
            # column
            concat = pd.concat([concat, df], axis = 1)  

        if(note != None):
            concat["Note"] = note

        # returns the full table with all the economic accounts as columns 
        return concat.reset_index(drop = False)