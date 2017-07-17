import numpy as np
import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt
import time

#to get the runtime of the program
start_time = time.time()

#storing the data in pandas data frame
df = pd.read_csv("subscription_report.csv", parse_dates = ['Transaction Date'])


#For Annual revenue
d = pd.DataFrame()
d['year'] = df['Transaction Date'].dt.year
d['Amount (USD)'] = df['Amount (USD)']
d = d.sort_values(by = 'year')

k = pd.DataFrame()
k['annual_revenue'] = d.groupby('year')['Amount (USD)'].sum()

k[1] = 0
k.columns = ['annual_revenue', 'revenue_growth']
for i in range(len(k)-1):
    k.iloc[i+1, 1] = (k.iloc[i+1, 0] - k.iloc[i, 0])*100/k.iloc[i, 0]

#years which had highest revenue growth and loss
year_max_growth = k['revenue_growth'].idxmax()
year_max_loss = k['revenue_growth'].idxmin()

print "Year which had maximum revenue growth : %d" %year_max_growth
print "Year which had maximum revenue loss : %d" %year_max_loss

#dropping unwanted columns
k = k.drop('revenue_growth', axis = 1)

#saving the output to annual_revenue.csv file
print "Saving annual revenues to annual_revenue.csv ..."
k.to_csv('annual_revenue.csv')

#subsetting the original dataframe for prediction and taking points after 1998 which shows linear trend
linear_data = k[k.index.values >= 1998]

#using linear regression to predict annual revenue for year 2015
x = linear_data.index.values
y = linear_data['annual_revenue']

#using numpy arrays to use in scikit learn's linear regression model
x = np.array([x]).T
y = np.array([y]).T

#regressor
regr = linear_model.LinearRegression()
regr.fit(x, y)

#predicted annual revenue for 2015
print "Predicted annual revenue for 2015: %d USD" % regr.predict(2015)


#For Subscription ID, Subscription time and Subscription type
df = df.drop('Amount (USD)', axis = 1)
df = df.sort_values(by = ['Subscription ID', 'Transaction Date'])

#first time subscription date
first_time = df.groupby('Subscription ID')['Transaction Date'].nsmallest(2).groupby(level = 'Subscription ID').first()
#second time subscription date
second_time = df.groupby('Subscription ID')['Transaction Date'].nsmallest(2).groupby(level = 'Subscription ID').last()
#last time subscription date
last_time = df.groupby('Subscription ID')['Transaction Date'].last()

#total subscription time
sub_time = last_time - first_time
#period of one subscription
sub_onetime = second_time - first_time

#changing data types from timedelta64 to float64
sub_time = sub_time / np.timedelta64(1, 'D')
sub_onetime = sub_onetime / np.timedelta64(1, 'D')

#concatenating sub_time and sub_onetime data frames to final dataframe
t = pd.concat([sub_time, sub_onetime], axis = 1)

#for loop to determine the subscription type
sub_type = []
for row in t[1]:
    if row == 0:
        sub_type.append('one-off')
    elif row == 1:
        sub_type.append('daily')
    elif (row == 365) | (row == 366):
        sub_type.append('yearly')
    else:
        sub_type.append('monthly')

#adding subscription type to final data frame
t['sub_type'] = sub_type
#naming columns
t.columns = ['Subscription time (days)', 'sub_onetime', 'Subscription type']
#dropping unwanted columns
t = t.drop('sub_onetime', axis = 1)
#saving the output to your_list.csv file
print "Saving subscription ids and type to subs_id_type.csv ..."
t.to_csv('subs_id_type.csv')


#runtime of the program
print "Run time of this program: %.2f seconds" %(time.time() - start_time)
#runitme is around 2 mins
