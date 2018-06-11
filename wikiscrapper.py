# -*- coding: utf-8 -*-
"""
Created on Sat Jun 09 18:52:00 2018

@author: Monica Shrestha
"""

from bs4 import BeautifulSoup as bs
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask,render_template

#using pandas read_html function to read all the tables in the page and store them in dataframe.

url = 'https://en.wikipedia.org/wiki/2018_Winter_Olympics_medal_table'
print ('Fetching url {}'.format(url))
df = pd.read_html(url)

#copying the dataframe with 2018 Winter Olympics medal to new dataframe
df1 = df[1].copy()

#since there there are more than one country with same rank, formatting dataframe to assign each country with the corresponding rank. 
for i in range(0,len(df1)):
    if pd.isnull(df1[df1.columns[-1]][i]):
    #if pd.isnull(df1[df1.columns[-1]][i]):
        df1.iloc[i] = df1.iloc[i].shift(1)
        if i!= len(df1)-1:
            df1.iloc[i][0] = df1.iloc[i-1][0]


#assgning fisrt row of dataframe as column name of dataframe and deleting the fisrt row
df1.columns = df1.iloc[0]
df1 = df1.reindex(df1.index.drop(0))

#re-indexing the dataframe after deleting the last row which contains the total of all.
df1 = df1.reindex(df1.index.drop(31))
df1 = df1.reset_index()
del df1['index']


#storing the dataframe into the database'wiki.db' (sqlite3) in the table name 'winter_olympic_2018' with NOC as primary key

#building the connection with the database and creating the cursor
print ('Connecting to database wiki.db')
conn = sqlite3.connect('wiki.db')
cur = conn.cursor()

#checking if the table already exists and creating one it not
cur.execute("CREATE TABLE IF NOT EXISTS winter_olympic_2018 (rank, noc varchar PRIMARY KEY, gold, silver, bronze, total)")

#passing dataframe to database
df1.to_sql('winter_olympic_2018', con = conn, if_exists = 'replace', index = False)

#checking if the table cintains all the data --optional
#cur.execute('select * from winter_olympic_2018').fetchall()

#closing the connection with the database
conn.close()


# assigning the top ten rank to the new datafarme 'df2'
df2 = df1[:10]

#creating a list of all columns to build the graph

print ('Creating multiline graph')
rank = list(df2['Rank'].map(lambda x:int(x)))
gold = list(df2['Gold'].map(lambda x:int(x)))
silver = list(df2['Silver'].map(lambda x:int(x)))
bronze = list(df2['Bronze'].map(lambda x:int(x)))
noc = list(df2['NOC'])


#creating the multiline graph of x-axis as 'NOC' and y-axis as 'gold', 'silver' and 'bronze'
plt.xticks(np.arange(min(rank), max(rank)+1, 1.0),noc,rotation=45)

plt.plot(rank, gold, c = 'gold', marker = 'o', label = 'gold')
plt.plot(rank, silver, c = 'silver', marker = 'o', label = 'silver')
plt.plot(rank, bronze, c = '#cc9966', marker = 'o', label = 'bronze')
plt.legend()
plt.show()

#using flask for web application to show and sort(ascending and descending) the table
app = Flask(__name__)

@app.route('/')
def displayTable():
    #connecting to database to get data from table
    conn = sqlite3.connect('wiki.db',check_same_thread=False)
    cur = conn.cursor()
    cur.execute('select * from winter_olympic_2018')
    items = cur.fetchall();
    conn.close()
    
    return render_template('wikitablesort.html', items = items)
 
if __name__ == '__main__':
    app.run('localhost', 8000, debug = True)







