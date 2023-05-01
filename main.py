import requests, os
import datetime as dt
from bs4 import BeautifulSoup
from Infinitydatabase import Infinitydatabase
import urllib3
urllib3.disable_warnings()

def holidays(*years):
    holidays =[]
    for year in years:
        url =f'https://www.tn.gov.in/holiday/{year}'
        response =requests.get(url, verify=False).text
        soup =BeautifulSoup(response, 'html.parser')
        for holiday in soup.findAll('div', {'class': 'holidayarc_res_odd'}):
            holiday =(
                holiday.find('div', {'class': 'harc_date'}).text.strip(),
                holiday.find('div', {'class': 'harc_name'}).text.strip()
            )
            holidays.append(holiday)
    return holidays

def getreal_date():
    date =dt.datetime.now()
    delta =dt.timedelta(hours=5, minutes=30)
    date =(date+delta)
    return date

def send_Notify(db, notify_table, Place, Level, Info):
    day =getreal_date()
    date =day.date()
    time =day.time()        
    result =db.query(f'select Times, NewDate, NewTime, OldDate, OldTime from {notify_table} where place="{Place}" and level="{Level}" and info="{Info}"')
    row =result['row']
    if row:
        times =row[0][0]; lastdate =row[0][1]; lasttime =row[0][2]
        olddate =row[0][3]; oldtime =row[0][4]
        query =f'update {notify_table} set Times={int(times)+1}, Notify=true'
        if olddate =='NULL' and oldtime =='NULL':
            query +=f', OldDate="{lastdate}", OldTime="{lasttime}"'
        query+=f', NewDate="{date.strftime(r"%Y-%m-%d")}", NewTime="{time.strftime("%H:%M %p")}" where place="{Place}" and level="{Level}" and info="{Info}"'
    else: query =f'insert into {notify_table} (Place, Level, NewDate, NewTime, Info) values ("{Place}", "{Level}", "{date.strftime(r"%Y-%m-%d")}", "{time.strftime("%H:%M %p")}", "{Info}")'
    return db.query(query)

def main():
    infdb =Infinitydatabase(os.environ['DB_ADMIN_URL'])
    today =getreal_date()
    for holiday in holidays(today.year):
        splits =holiday[0].split()
        month =dt.datetime.strptime(splits[0], "%b").month
        date = int(splits[1])
        leaveday =dt.datetime(today.year, month, date)
        if today.strftime('%y/%m/%d') == leaveday.strftime('%y/%m/%d'):
            send_Notify(infdb, 'Notifier', 'Holidays-Notifier', 'Info-Happy', f'Today: {holiday[1]}, so Leave..')
            print(f'Today: {holiday[1]}, so Leave..')
        elif today.strftime('%y/%m/%d') < leaveday.strftime('%y/%m/%d') and (dt.timedelta(days=os.environ['ALERT_WITHIN_DAY'])+today).strftime('%y/%m/%d') > leaveday.strftime('%y/%m/%d'):
            send_Notify(infdb, 'Notifier', 'Holidays-Notifier', 'Info-Happy', f'{holiday[0]} on {holiday[1]}, so Alert..')
            print(f'{holiday[0]} on {holiday[1]}, so Alert..')

if __name__ == '__main__':
    main()
