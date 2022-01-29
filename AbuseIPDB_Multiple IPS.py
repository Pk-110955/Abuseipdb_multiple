import csv
from bs4 import BeautifulSoup
import requests
from IPython.core.display import display
import pandas as pd
from pandas import Series, DataFrame

def abuseipdbChecker(url):
    # e.g. url = "https://www.abuseipdb.com/check/220.191.211.7"
    #      url = "https://www.abuseipdb.com/check/baidu.com"
    # HTTP Query
    myResult = requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'})
    printResult = ''
    print ("[.] AbuseIPDB Result:")

    # if the input value is invalid, such as 'baidu.comx', 'x.x.x.x.x', etc.
    # Invalid Input: '422 Unprocessable Entity'
    if myResult.status_code == 422:
        print ('Error: 422 Unprocessable Entity (e.g. http://www.com)')
        print ("We expected a valid IP address or Domain name.")
        exit()
    else:
        # If domain resolved to an IP
        if url != myResult.url:
            print ("Your request has been resolved to ") + myResult.url
        c = myResult.content
        soup = BeautifulSoup(c, "lxml")

        # Part 1: Locate the reporting times that we want
        # reportTimes = soup.find_all(class_="well")
        mySoup = soup.find('div', {'class': 'col-md-6'})

        # Http Response code is still 200 but we got a message:
        #      'We can't resolve the domain www.comz! Please try your query again.'
        if mySoup is None:
            print ('We expected a valid IP address or Domain name.')
        else:
            # Get the first 'p' tag in <div class="well">
            # You can only put 'find_all' after 'find'
            pTag = mySoup.find('p')
            reportTimes = pTag.find('b')

            # Print reporting times
            try:
                if soup.findAll('div', {'class': 'col-md-6'})[2].find('p').find('b').string == "Important Note:":
                    print ("Note: You probably input a private IP. Please check again ...")
                else:
                    print ("Reported  :" + soup.findAll('div', {'class': 'col-md-6'})[2].find('p').find('b').string + " times")
                    print ("Confidence of Abuse is :  "+ soup.findAll('div', {'class': 'col-md-6'})[2].find('p').find_all('b')[1].string)
                    print ("ISP      :"+ soup.findAll('div', {'class': 'col-md-6'})[2].findAll('tr')[0].find('td').string)
                    print ("Usage type    :"+ soup.findAll('div', {'class': 'col-md-6'})[2].findAll('tr')[1].find('td').string)
                    print ("Domain      :"+ soup.findAll('div', {'class': 'col-md-6'})[2].findAll('tr')[2].find('td').string)
                    print ("Country      :"+ soup.findAll('div', {'class': 'col-md-6'})[2].findAll('tr')[3].findAll('td')[0].text)
                    print ("City      :"+ soup.findAll('div', {'class': 'col-md-6'})[2].findAll('tr')[4].find('td').string)
                    
                    printResult = 'Reported ' + soup.findAll('div', {'class': 'col-md-6'})[2].find('p').find('b').string + ' times'
            # if result equals 'None'
            except Exception:
                reportTimes = 0
                #print ('Reported ' + str(reportTimes) + ' times')
                #printResult = 'Reported ' + str(reportTimes) + ' times'
                print ('')

            # Part 2: Locate the table that we want
            tables = soup.find_all(class_="table table-striped responsive-table")

            if tables != []:
                # Use BeautifulSoup to find the table entries with a For Loop
                rawData = []

                # Looking for every row in a table
                # table[0] is just the format for BeautifulSoup
                rows = tables[0].findAll('tr')

                for tr in rows:
                    cols = tr.findAll('td')
                    for td in cols:
                        # data-title = "Reporter"
                        text = cols[0].text
                        rawData.append(text)
                        # data-title = "Date"
                        text = cols[1].text
                        rawData.append(text)
                        '''
                        # data-title = "Comment" (Ingnored)
                        text = cols[2].text
                        rawData.append(text)
                        '''
                        # data-title = "Categories"
                        text = cols[3].text + '\n'
                        rawData.append(text)

                # Modify rawData
                reporter = []
                date = []
                category = []

                itemNum = len(rawData)
                index = 0

                # For 'reporter'
                index1 = 0
                # For 'date'
                index2 = 1
                # For 'category'
                index3 = 2

                for index in range(0, itemNum - 1):
                    # Make sure this loop will not exceed the limit
                    if index1 <= itemNum - 3:
                        # Reporter
                        reporter.append(rawData[index1].replace('\n', ''))
                        index1 += 3

                        # Date
                        date.append(rawData[index2].replace('\n', ''))
                        index2 += 3

                        # Category
                        category.append(rawData[index3].replace('\n\n', ' | ').replace('\n', ' | '))
                        index3 += 3

                        # Global Index
                        index += 1

                # Panda Series
                reporter = Series(reporter)
                date = Series(date)
                category = Series(category)

                # Concatenate into a DataFrame
                pd.set_option('display.width', 5000)
                legislative_df = pd.concat([date, reporter, category], axis=1)

                # Set up the columns
                legislative_df.columns = ['Date', 'Reporter', 'Category']

                # Delete the dups and reset index (and drop the old index)
                legislative_df = legislative_df.drop_duplicates().reset_index(drop=True)


                display(legislative_df)

                print ('')
    return printResult


# Starting..........
print '\n Enter file path with file name '

print '\n Eg: /Users/pk/Desktop/IP.csv '

k=open(raw_input('\n Enter CSV file path :'))

csvreader = csv.reader(k)
header = next(csvreader)
rows = []

for row in csvreader:
    rows.append(row)
    
for ip in rows:
    try:
        print 'https://www.abuseipdb.com/check/'+str(ip)
        abuseipdbChecker('https://www.abuseipdb.com/check/'+str(ip[0]))

    except:
        print 'input error'


