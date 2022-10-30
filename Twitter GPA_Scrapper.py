#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tweepy 
import pandas as pd
import datetime
import pytz
import re
import requests
import sys
from pytz import timezone
import time


# In[ ]:


handles = pd.read_excel('twitter_handles.xlsx')
handles_list = list(handles['Twitter Handles'])


# In[ ]:


consumer_key = "xxxxx"
consumer_secret = "xxxxx"
access_token = "xxxxx"
access_token_secret = "xxxxxx"


# In[ ]:


#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
API = tweepy.API(auth,wait_on_rate_limit=True,retry_count = 5, retry_delay = 5)


# In[ ]:


def authenticate_tokens(api):
    counter = 1
    while True:
        try:
            print("Authenticating your API......")
            API.verify_credentials()
            print('Successfully Authenticated')
            return True
        except:
            print('\nAuthentication Failed.......retrying to check again')
            if counter <3:
                counter = counter+1
                for x in range(10):   
                    print(('\rRetrying in {} sec').format(-(x-10)), end = '')
                    time.sleep(1)
                continue
            else:
                print('\nAuthentication Has Failed, check your authentication tokens and try again')
                return False
                break
        else:
            return False


# In[ ]:


def check_internet_connection():
    url = "http://www.google.com"
    timeout = 5
    counter = 1    
    while True:
        try:
            request = requests.get(url, timeout=timeout)
            if (request.status_code == 200):
                return True
        except:
            print("\nSeems there is no internet connection..........retrying")
            continue
        else:  
            print('\nThere is no internet connection, check and try again')
            return False


# In[ ]:


def check_if_user_exist(screen_name, api):
    "'This function checks if a twiter screen name given exists on twitter'"   
    
    counter = 1
    while True:
        try:
            user = (api.get_user(screen_name = screen_name)).name 
            return True
        except:
            print('seems',screen_name,'profile can\'t be traced on twitter.......retrying to trace the acount again')
            if counter <4:
                counter = counter+1
                continue                
            else:
                print(screen_name,'is not on twitter. Proceeding with other users......')
                return False
                break
        else:
            print(screen_name,'is not on twitter. Proceeding with other users......')
            return False


# In[ ]:


def retrive_GPA(df, final_df):
    "This function retrieves GPA from twitter user description"
    while True:
        try:   
            
            for i in range(len(df)):
                original_string = str(df['DESCRIPTION'].iloc[i])
                string = (str(df['DESCRIPTION'].iloc[i])).lower()
                handle = df['TWITTER HANDLE'].iloc[i]
                if(original_string == 'The user seem not to be on twitter, check again!'):
                    final_gpa = 'INVALID'
                elif (original_string == ''):
                    final_gpa = 'None'                    
                else:
                    final_gpa = 'None'

                if 'gpa' in string:
                    string = string.replace('/4.0','')
                    p = string.index('gpa')

                    sub_str_l = string[p-2:p]
                    sub_str_r = string[p:p+6]
                    if('|' in sub_str_l ):
                        sub_str = string[p:p+9]
                    elif('|' in sub_str_r):
                        sub_str = string[p-5:p]
                    else:
                        sub_str = string[p-5:p+12]
                        
                    try:
                        if(len(sub_str)==0):
                            gpa = (re.findall('[1-4]\.\d+', string))
                        else:
                            gpa = (re.findall('[1-4]\.\d+', sub_str))
                    except:
                        gpa = (re.findall('[1-4]\.\d+', string))

                    if(len(gpa)==0):
                        gpa = (re.findall('[1-4]\.\d+', string))
                    gpas = [float(x) for x in gpa]

                    if (len(gpas)>1):
                        if(gpas[0]>5):
                            final_gpa = gpas[1]
                        else:
                            final_gpa = gpas[0]
                    else:
                        final_gpa = gpas[0]
                final_df.loc[len(final_df.index)] = [handle,str(final_gpa),original_string] 
            print('DONE')
            return final_df
            break
        except Exception as e:
            print(e)
            print('Please be patient as the system retries....')
            for x in range(60):   
                print(('\rRetrying in {} sec').format(-(x-60)), end = '')
                time.sleep(1)
            continue


# In[ ]:


def pull_desc(screen_name,api):
    user = '@'+str(screen_name)
    while True:
        try:
            desc = (api.get_user(screen_name = user)).description
        except Exception as e:
            print('Something went wrong pulling the description system retrying....')
            for x in range(10):   
                print(('\rRetrying in {} sec').format(-(x-10)), end = '')
                time.sleep(1)
            continue
        return desc


# In[ ]:


desc_df = pd.DataFrame(columns = ['TWITTER HANDLE', 'DESCRIPTION'])


# In[ ]:


GPA_df = pd.DataFrame(columns = ['TWITTER HANDLE', 'GPA','DESCRIPTION'])


# In[ ]:


count = 1 
if (check_internet_connection()):
    if(authenticate_tokens(API)):
        print('Pulling description from twitter handles..')
        for item in handles_list: 
            if (check_internet_connection()):                
                print(item,': Number',count,'of',len(handles_list),'handles')
                item = str(item)
                if item == 'nan':
                    desc = ''
                    item = ''
                    desc_df.loc[len(desc_df.index)] = [item,desc]
                    count +=1
                    print('----------------------------------------')
                else:
                    if(check_if_user_exist(item, API)):
                        desc = pull_desc(item,API)
                        desc_df.loc[len(desc_df.index)] = [item,desc]
                        count +=1
                        print('----------------------------------------')
                    else:
                        desc = 'The user seem not to be on twitter, check again!'
                        desc_df.loc[len(desc_df.index)] = [item,desc]
                        count +=1
                        print('----------------------------------------')


# In[ ]:


Final_DF = retrive_GPA(desc_df, GPA_df)


# In[ ]:


Final_DF.to_excel("GPA_final.xlsx")  
print('Data written successfully to Excel doc named GPA_final.xlsx')

