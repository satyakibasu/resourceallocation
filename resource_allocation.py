# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:52:47 2021

@author: H08475008
"""

import pandas as pd
import datetime


'''
#This program helps to find the resource availability between 2 input date ranges
#against the current allocation period of a resource.

#Test cases
1. Input End date within one of the max end date e.g. end_date = 17/10/2021
2. Input End date greater than the max end date e.g. end_date = 24/10/2021
3. Test with multiple rows (say 3)
4. Input Start date less than min of end date e.g. start_date = 24/09/2021
5. Input Start date greater than Start date e.g. start_date = 03/10/2021
6. input dates are outside the Start n End Date of a resource

# Test Data
Project Name	Resource Name	Resource Type	Resource BRID	Start Date	End Date	Percentage Allocation
Project A	Sumit Dhadwade	Perm	G01333807	1-Oct-21	15-Oct-21	60%
Project B	Sumit Dhadwade	Perm	G01333807	16-Oct-21	18-Oct-21	40%
Project C	Sumit Dhadwade	Perm	G01333807	16-Oct-21	18-Oct-21	20%
Project B	Sumit Dhadwade	Perm	G01333807	19-Oct-21	21-Oct-21	10%
Project C	Pasu Ramasamy	Perm	G01016406	1-Nov-21	31-Dec-21	50%
Project D	Pasu Ramasamy	Perm	G01016406	1-Nov-21	31-Dec-21	50%

'''

#Function to select the rows that is applicable for calculation
def resourceAllocation(row, in_start_date, in_end_date):
    start_flag = 'N'
    end_flag = 'N'
    indicator_flag = 'N' #introduced to check if a dataframe has already been picked for a resource
    
    # This is for Case 2,3
    if (row['Start Date'] <= in_start_date) and row['End Date'] >= in_start_date:
        indicator_flag = 'Y'
        start_flag = 'Y'
    
    #This is for Case 1,2
    if (row['Start Date'] <= in_end_date) and row['End Date'] >= in_end_date:
        indicator_flag = 'Y'
        end_flag = 'Y'
    
    if start_flag == 'Y' or end_flag == 'Y':
        row["Indicator Flag"] = indicator_flag
        return(row)
        
    # This is for Case 1,3,4
    if in_end_date > row['End Date'] and start_flag == 'N' and end_flag == 'N' and in_start_date <= row['Start Date']:
        indicator_flag = 'Y'
        row["Indicator Flag"] = indicator_flag
        return(row)
    
    # This is for Case 1,2,5
    if in_start_date < row['Start Date'] and in_end_date < row['End Date'] and start_flag == 'N' and end_flag == 'N' and indicator_flag == 'N':
        index_ = ['Resource Name', 'Start Date', 'End Date','Percentage Allocation','Indicator Flag']
        sr = pd.Series([row['Resource Name'], in_start_date, in_end_date,0.0,indicator_flag])
        sr.index = index_
        return(sr)
    
    # This is for Case 6
    if in_start_date > row['Start Date'] and in_end_date > row['End Date'] and start_flag == 'N' and end_flag == 'N':
        index1_ = ['Resource Name', 'Start Date', 'End Date','Percentage Allocation','Indicator Flag']
        sr1 = pd.Series([row['Resource Name'], in_start_date, in_end_date,0.0,indicator_flag])
        sr1.index = index1_
        return(sr1)
        

    
if __name__=="__main__":
        
    #Capture the input fields
    in_start_date = '24-10-2021'
    in_end_date = '26-10-2021'
    
    #Read the excel file
    df = pd.read_excel('DADM.xlsx', sheet_name='Sheet3',dtype=str)
    
    #Convert all str dates into datetime objects
    df['Start Date'] = pd.to_datetime(df['Start Date'], format='%Y-%m-%d')
    df['End Date'] = pd.to_datetime(df['End Date'], format='%Y-%m-%d')
    df['Percentage Allocation'] = df['Percentage Allocation'].astype(float)
    in_start_date = datetime.datetime.strptime(in_start_date,'%d-%m-%Y')
    in_end_date = datetime.datetime.strptime(in_end_date,'%d-%m-%Y')
    
    #select the rows for the input resource
    resource_list = ['Sumit Dhadwade']
    if resource_list:
        r_df = df[df['Resource Name'].isin(resource_list)][['Resource Name','Start Date','End Date','Percentage Allocation']]
    else:
        r_df = df[['Resource Name','Start Date','End Date','Percentage Allocation']]
    r_df = r_df.dropna(axis=0) 
    
    dfs = []
    group_resource = r_df.groupby(['Resource Name'])
    for resource, group in group_resource:
        
        new_group = group.groupby(['Resource Name','Start Date','End Date'])['Percentage Allocation'].sum()
        group = pd.DataFrame([new_group]).transpose().reset_index()

        #get the maximum and minimum start n end dates for this dataframe
        m = group['Start Date'].min()
        n = group['End Date'].max()

        #Apply the function to select the rows based on input criteria
        f = group.apply(resourceAllocation, axis=1, in_start_date=in_start_date,in_end_date=in_end_date)
        f = f[pd.notnull(f['Start Date'])]
               
        found = f[f['Indicator Flag'].str.contains('Y')]
        if len(found) > 0:
            f = f[(f['Percentage Allocation'] != 0.0)]

        f = f.drop('Indicator Flag', axis=1)
        
     

    #Create a new record if input date is less than min start date
        d = dict()
        d2 = dict()
        if in_start_date < m:
            d['Start Date'] = in_start_date
            d['End Date'] = m - pd.to_timedelta(1,unit='d')
            d['Resource Name'] = resource
            d['Percentage Allocation'] = 0
            c = pd.DataFrame.from_dict(d,orient ='index').transpose()
            f = pd.concat([f,c], axis=0)
         
        #Create a new record if input date is more than max end date
        if in_end_date > n:
            d2['Start Date'] = n + pd.to_timedelta(1,unit='d')
            d2['End Date'] = in_end_date
            d2['Resource Name'] = resource
            d2['Percentage Allocation'] = 0
            c = pd.DataFrame.from_dict(d2,orient ='index').transpose()
            f = pd.concat([f,c], axis=0)
                
        
        #Replace the Start n End dates with the input dates based on citeria
        f.loc[f['Start Date'] < in_start_date, 'Start Date'] = in_start_date
        f.loc[f['End Date'] > in_end_date, 'End Date'] = in_end_date
        
        #Optional fields
        #f['Input Start Date'] = in_start_date
        #f['Input End Date'] = in_end_date
 
        dfs.append(f)
    
    final_df = pd.concat([df for df in dfs], axis = 0)
    final_df = final_df.drop_duplicates()
   
    #Calculate the work that can be allocation
    final_df["can work"] = 1.0 - final_df["Percentage Allocation"].astype(float)
    final_df = final_df.sort_values(by=['Resource Name','Start Date'], ascending = True)
    final_df = final_df.reset_index()
    final_df = final_df[final_df['can work'] > 0.0][['Resource Name','Start Date', 'End Date', 'can work']]
    print(final_df)
    