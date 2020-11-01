import pandas as pd 
import os

pd.options.mode.chained_assignment = None


#make sure csv's are in a folder label'ed csv 
def grab_csvs(list_of_sheets): 
        csvs = []
        
        #loop over csvs in csv folder
        for sheet in list_of_sheets: 
            try:
                csv_sheet = pd.read_csv('./csv/' + sheet)
                csvs.append(csv_sheet)
            except FileNotFoundError:
                raise 'It appears that your files are not labelled correctly or not stored in a folder labelled csv.'

        #order csvs: slcsp, zips, plans
        while len(csvs[0].columns) > len(csvs[1].columns):
            longer = csvs[0]
            del csvs[0]
            csvs.append(longer)

        return csvs


#find the second lowest silver plan for zipcode
#load in the `slcsp.csv` and `zips.csv` spreadsheets, finding the states and rate areas for zips in  `slcsp.csv`

def filter_csv(x, y):
    
    #create lists to hold our looped values
    found_zips = []
    lists_built = []

    #create empty dateframe to hold our zips and their respective states and rate areas
    zip_state_areas = pd.DataFrame(columns=['zipcode', 'state', 'rate_area'])

    #find the rows in zips.csv that match the zips in slcsp.csv
    for zipcode in x['zipcode']:
        zipcode = int(str(zipcode).zfill(5))
        zip_found = y.loc[y['zipcode'] == zipcode]
        found_zips.append(zip_found.values.tolist())

    #filter out all the zip codes that cover multiple rate areas 
    for each_zip in found_zips:
        state_rate_areas = []

        #grab the fifth item of the list(s)--the rate area
        for j in each_zip:
            state_rate_areas.append(j[4]) 


        #for zip codes with only one unique rate area: create a list of the zipcode(each_zip[0][0]), state(each_zip[0][1]), and rate areas (state_rate_area[0])
        if len(set(state_rate_areas)) == 1:
            list_build = []
            list_build.append(each_zip[0][0])
            list_build.append(each_zip[0][1])
            list_build.append(state_rate_areas[0]) 

            #append each list_build to an object of lists
            lists_built.append(list_build)

    #take the object of lists and feed it to the empty data frame
    for i in range(len(lists_built)):
        zip_state_areas.loc[i] = [lists_built[i][0]] + [lists_built[i][1]] + [lists_built[i][2]]
    
    return zip_state_areas


def find_rates(x, y, z):

    #filter plans.csv for only the Silver plan
    y = y.loc[y['metal_level'] == 'Silver']
    
    #combine the zip_state_areas with the Silver plans
    merged_rates = pd.merge(x, y, on=['state', 'rate_area'], how='left')

    #create a dataframe of each zip and a list of the unique rates charged for the silver plan
    sorted_rates = merged_rates.groupby('zipcode')['rate'].unique().reset_index()

    #find the second lowest silver rate plan for each zipcode
    for zipcode in sorted_rates['zipcode']:
        zip_rates = sorted_rates.loc[sorted_rates['zipcode'] == zipcode]
        for rates in zip_rates['rate']:

            #only look at zipcodes that have more than one rate for the silver plans
            if len(rates) > 1: 
                rates = sorted(rates)

                #add the second lowest rate to the empty rate column in slcsp.csv
                z.loc[z['zipcode'] == zipcode, 'rate'] = '{:.2f}'.format(rates[1])
    
    return z

def main():

    my_csvs = []

    #check to make sure csv folder is in it directory
    if os.path.isdir('./csv'):
        for files in os.listdir("./csv"):
            my_csvs.append(files)
    else:
        raise 'You do not have a csv folder in this directory.  Please read readme on '

    #check to make sure proper csv files are in csv folder
    if set(my_csvs) == set(['slcsp.csv', 'zips.csv', 'plans.csv']):

        loaded_csvs = grab_csvs(my_csvs)

        csv1 = loaded_csvs[0]
        csv2 = loaded_csvs[1]
        csv3 = loaded_csvs[2]

        state_areas = filter_csv(csv1, csv2)
        rates_found = find_rates(state_areas, csv3, csv1)

        rates_found.to_csv('stdout.csv', index=False)
    else: 
        raise 'Your csv folder does not appear to contain only the correct csv files: slcsp.csv, plans.csv, zips.csv'

    print('Rates found. Please check stdout.csv')
main()
