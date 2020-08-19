from app import app
import datetime as dt
from pprint import pprint
import os, time
import requests
import json
import sys
import subprocess
import os
import random
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime, timedelta
from flask import Flask
from flask import request
import configparser

adminEmailList = ['email1@mail.com', 'email2@mail.com']

# read variables from config
credential = configparser.ConfigParser()
credential.read('cred')

bearer = credential['Webex']['WEBEX_TEAMS_TOKEN']
botEmail = credential['Webex']['WEBEX_BOT_EMAIL']
ROOM_ID_REPORT = credential['Webex']['WEBEX_TEAMS_ROOM_ID_REPORT']
# WebhookUrl
webhookUrl = credential['Webex']['WEBEX_WEBHOOK_URL']

# Set your custom report time (24-hour format)
reportTime = credential['Parameters']['REPORT_TIME']
# Enter capacity of working place
capacity = int(credential['Parameters']['CAPACITY'])

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + bearer
}

#### Functions

def createWebhook(bearer, webhookUrl):
    hook = True
    botWebhooks = send_webex_get("https://webexapis.com/v1/webhooks")["items"]
    for webhook in botWebhooks:
        if webhook["targetUrl"] == webhookUrl:
            hook = False
    if hook:
        dataWebhook = {
        "name": "Messages collab bot Webhook",
        "resource": "messages",
        "event": "created",
        "targetUrl": webhookUrl
        }
        dataWebhookCard = {
            "name": "Card Report collab bot Webhook",
            "targetUrl": webhookUrl,
            "resource": "attachmentActions",
            "event": "created"
        }
        send_webex_post("https://api.ciscospark.com/v1/webhooks/", dataWebhook)
        send_webex_post("https://webexapis.com/v1/webhooks/", dataWebhookCard)
    print("Webhook status: done")

def send_webex_get(url, payload=None,js=True):

    if payload == None:
        request = requests.get(url, headers=headers)
    else:
        request = requests.get(url, headers=headers, params=payload)
    if js == True:
        if request.status_code == 200:
            try:
                r = request.json()
            except json.decoder.JSONDecodeError:
                print("Error JSONDecodeError")
                return("Error JSONDecodeError")
            return r
        else:
            print (request)
            return ("Error " + str(request.status_code))
    return request


def send_webex_post(url, data):

    request = requests.post(url, json.dumps(data), headers=headers).json()
    return request

def bookingWorkplaceForDay(personId, day):
    resp = send_webex_get('https://webexapis.com/v1/people/' + personId)
    if int(checkFreePlaces(day)):
        if isAlreadyBooked(day, resp["displayName"], personId) != True:
            return True
        appendList(resp["displayName"], day)
        greetingsBooked(personId, msg='', date=day)
    else:
        excessCapacityNotification(personId)


def isAlreadyBooked(date , name, personId):
    if date == 'today':
        with open("today.txt", "r") as f:
            list = f.read()
    elif date == 'tomorrow':
        with open("tomorrow.txt", "r") as f:
            list = f.read()
    elif date == 'after tomorrow':
        with open("after_tomorrow.txt", "r") as f:
            list = f.read()
    if list == '':
        return True
    if (name in list.split('\n')):
        greetingsBooked(toPerson=personId, msg=' # You have already booked a place earlier')
        return False
    return True

def checkFreePlaces(date):
    if date == 'today':
        with open("today.txt", "r") as f:
            list = f.read()
    elif date == 'tomorrow':
        with open("tomorrow.txt", "r") as f:
            list = f.read()
    elif date == 'after tomorrow':
        with open("after_tomorrow.txt", "r") as f:
            list = f.read()
    if (capacity - (len(list.split('\n')) - 1)) <= 0:
        return (str(0))
    return (str(capacity - (len(list.split('\n')) - 1)))

def postCard(personEmail):
    # open and read data from file as part of body for request
    with open("cardText.txt", "r", encoding="utf-8") as f:
        data = f.read().replace('USER_EMAIL', personEmail)
    # Add encoding, if you use non-Latin characters
    data = data.encode("utf-8")
    request = requests.post('https://webexapis.com/v1/messages', data=data, headers=headers).json()
    print("POST CARD TO ", personEmail)

def greetingsBooked(toPerson, msg='', date=''):
        if msg == '' and date != '':
            with open("sentence_done.txt", "r+") as f:
                greetings = random.choice(f.read().split('\n'))
                if date == 'today':
                    date = (datetime.now()).strftime('%d/%m/%Y')
                elif date == 'tomorrow':
                    date = (datetime.now() + timedelta(1)).strftime('%d/%m/%Y')
                elif date == 'after tomorrow':
                    date = (datetime.now() + timedelta(2)).strftime('%d/%m/%Y')
                msg = " # Thanks, the workplace on {} is reserved \n".format(date) + greetings
        if '@' in toPerson:
            body = {
                "toPersonEmail": toPerson,
                # Markdown text
                "markdown": msg,
                # This text would be displayed by Webex Teams clients that do not support markdown.
                "text": "This text would be displayed by Webex Teams clients that do not support markdown."
                }
        else:
            body = {
                "toPersonId": toPerson,
                # Markdown text
                "markdown": msg,
                # This text would be displayed by Webex Teams clients that do not support markdown.
                "text": "This text would be displayed by Webex Teams clients that do not support markdown."
                }
        send_webex_post('https://webexapis.com/v1/messages', body)


def appendList(employee, date):
    if date == 'today':
        with open("today.txt", "a") as f:
            f.write(employee + '\n')
    elif date == 'tomorrow':
        with open("tomorrow.txt", "a") as f:
            f.write(employee + '\n')
    elif date == 'after tomorrow':
        with open("after_tomorrow.txt", "a") as f:
            f.write(employee + '\n')

def getlist(date):
    if date == 'today':
        with open("today.txt", "r+") as f:
            return f.read().replace('\n', '\n\n')
    elif date == 'tomorrow':
        with open("tomorrow.txt", "r+") as f:
            return f.read().replace('\n', '\n\n')
    elif date == 'after tomorrow':
        with open("after_tomorrow.txt", "r+") as f:
            return f.read().replace('\n', '\n\n')

def excessCapacityNotification(personId):
    body = {
        "toPersonId": personId,
        # Markdown text
        "markdown": "Sorry, all seats have already booked for this day. Try to choose another day, or booking a meeting room. In case of an emergency, contact the lobby.",
        # This text would be displayed by Webex Teams clients that do not support markdown.
        "text": "This text would be displayed by Webex Teams clients that do not support markdown."
    }
    send_webex_post('https://webexapis.com/v1/messages', body)


def printList(personEmail):
    if True:
        reportText = " # Date: {} (today) \n # Empty seats: {}  \n Bookings: \n\n {} \n " \
                     " #Date: {} (tomorrow) \n # Empty seats: {}  \n Bookings: \n\n {} \n" \
                     " # Date: {} (after tomorrow) \n # Empty seats: {}  \n Bookings: \n\n {} \n".format(
                    str(datetime.now().strftime('%d/%m/%Y')), checkFreePlaces('today') , getlist('today'),
                    str((datetime.now() + timedelta(1)).strftime('%d/%m/%Y')), checkFreePlaces('tomorrow'), getlist('tomorrow'),
                    str((datetime.now() + timedelta(2)).strftime('%d/%m/%Y')), checkFreePlaces('after tomorrow'), getlist('after tomorrow'))
        print("-----------------------------REPORT TEXT------------------------------", reportText)
        reportText = " # Date: {} (today) \n # Empty seats: {}  \n Booking: \n\n {} \n " \
                 " #Date: {} (tomorrow) \n # Empty seats: {}  \n Booking: \n\n {} \n" \
                 " # Date: {} (after tomorrow) \n # Empty seats: {}  \n Booking: \n\n {} \n".format(
        str(datetime.now().strftime('%d/%m/%Y')), checkFreePlaces('today'), getlist('today'),
        str((datetime.now() + timedelta(1)).strftime('%d/%m/%Y')), checkFreePlaces('tomorrow'), getlist('tomorrow'),
        str((datetime.now() + timedelta(2)).strftime('%d/%m/%Y')), checkFreePlaces('after tomorrow'),
        getlist('after tomorrow'))
        
        body = {
        "toPersonEmail": personEmail,
        # Markdown text
        "markdown": reportText,
        # This text would be displayed by Webex Teams clients that do not support markdown.
        "text": "This text would be displayed by Webex Teams clients that do not support markdown."
        }
        send_webex_post('https://webexapis.com/v1/messages', body)


def informingCard(personEmail):
    with open("cardText_Inform.txt", "r", encoding="utf-8") as f:
        data = f.read().replace('USER_EMAIL', personEmail)
    # Add encoding, if you use non-Latin characters                                                                                                                                                           
    data = data.encode("utf-8")
    request = requests.post('https://webexapis.com/v1/messages', data=data, headers=headers).json()


def informingEmployees(data):
    body = {
        "toPersonId" : data['personId'],
        "text" : data['inputs']['Inform_text'],
        "files" : [ data['inputs']['img_url']  ]
    }
    if data['inputs']["button"] == 'test_inform':
        send_webex_post('https://webexapis.com/v1/messages', body)
    elif data['inputs']["button"] == 'send_inform':
        with open('employeesEmail.txt', 'r') as f:
            emailList = f.read().split('\n')
        print("Email List", emailList)
        for email in emailList:
                body = {
                    "toPersonEmail" : email,
                    "text" : data['inputs']['Inform_text'],
                    "files" : [ data['inputs']['img_url']  ]
                }
                send_webex_post('https://webexapis.com/v1/messages', body)
    
@app.route('/', methods=['GET', 'POST'])
def webex_webhook():
    if request.method == 'POST':
        webhook = request.get_json(silent=True)
        print("Webhook:")
        pprint(webhook)
        msg = 'Date for Booking'
        if webhook['resource'] == 'messages' and webhook['data']['personEmail'] != botEmail:
            result = send_webex_get('https://webexapis.com/v1/messages/{0}'.format(webhook['data']['id']))
            print("result messages", result)
            in_message = result.get('text', '').lower()
            if in_message.startswith('/list'):
                personEmail = webhook['data']['personEmail']
                print("/list email ", personEmail)
                printList(personEmail)
            elif in_message.startswith('/inform') and (webhook['data']['personEmail'] in adminEmailList):
                informingCard(webhook['data']['personEmail'])
            else:
                postCard(webhook['data']['personEmail'])
        elif webhook['resource'] == 'attachmentActions':
            result = send_webex_get('https://webexapis.com/v1/attachment/actions/{}'.format(webhook['data']['id']))
            print("RESULT ",result)
            if result['inputs']['button'] == 'today':
                bookingWorkplaceForDay(result['personId'], 'today')
            elif result['inputs']['button'] == 'tomorrow':
                bookingWorkplaceForDay(result['personId'], 'tomorrow')
            elif result['inputs']['button'] == 'after tomorrow':
                bookingWorkplaceForDay(result['personId'], 'after tomorrow')
            elif result['inputs']['button'] == 'free space':
                print("HERE FREE SPACE")
                reportText = "Empty seats \n # Today - {} \n  # Tomorrow - {} \n # After tomorrow - {}".format(checkFreePlaces('today'), checkFreePlaces('tomorrow'), checkFreePlaces('after tomorrow'))
                body = {
                    "toPersonId": result['personId'],
                    # Markdown text
                    "markdown": reportText,
                    # This text would be displayed by Webex Teams clients that do not support markdown.
                    "text": "This text would be displayed by Webex Teams clients that do not support markdown."
                }
                send_webex_post('https://webexapis.com/v1/messages', body)
            elif result['inputs']['button'] == 'test_inform' or result['inputs']['button'] == 'send_inform':
                informingEmployees(result)
        return "true"
    elif request.method == 'GET':
        message = "<center><img src=\"http://bit.ly/SparkBot-512x512\" alt=\"Webex Bot\" style=\"width:256; height:256;\"</center>" \
                  "<center><h2><b>Congratulations! Your <i style=\"color:#ff8000;\"></i> bot is up and running.</b></h2></center>" \
                  "<center><b><i>Please don't forget to create Webhooks to start receiving events from Webex Teams!</i></b></center>"
        return message

def lastReportDate(date=''):
    if date == '':
        with open("lastReportDate.txt", "r") as f:
            timeList = f.read().split(',')
            print ("Timelist", timeList)
            return (dt.datetime(int(timeList[0]), int(timeList[1]), int(timeList[2])))
    else:
        with open("lastReportDate.txt", "w") as f:
            print("Write date", date)
            f.write(str(date))

def clearLists(listName):
    if listName == 'all':
        open('today.txt', 'w').close()
        open('tomorrow.txt', 'w').close()
        open('after_tomorrow.txt', 'w').close()
    else:
        open(listName, 'w').close()

def editLists():
    print("Last report date in editLists ", lastReportDate())
    currentDate = datetime.now().strftime('%Y, %m, %d').split(',')
    today = dt.datetime(int(currentDate[0]), int(currentDate[1]), int(currentDate[2]))
    if ((lastReportDate() < today) and (datetime.now().strftime('%H:%M') > reportTime)):
        reportText = " # Date: {} (today) \n # Empty seats: {}  \n Booking: \n\n {} \n " \
                 " #Date: {} (tomorrow) \n # Empty seats: {}  \n Booking: \n\n {} \n" \
                 " # Date: {} (after tomorrow) \n # Empty seats: {}  \n Booking: \n\n {} \n".format(
        str(datetime.now().strftime('%d/%m/%Y')), checkFreePlaces('today'), getlist('today'),
        str((datetime.now() + timedelta(1)).strftime('%d/%m/%Y')), checkFreePlaces('tomorrow'), getlist('tomorrow'),
        str((datetime.now() + timedelta(2)).strftime('%d/%m/%Y')), checkFreePlaces('after tomorrow'),
        getlist('after tomorrow'))

        body = {
        "roomId": ROOM_ID_REPORT,
        # Markdown text
        "markdown": reportText,
        # This text would be displayed by Webex Teams clients that do not support markdown.
        "text": "This text would be displayed by Webex Teams clients that do not support markdown."
        }   
        send_webex_post('https://webexapis.com/v1/messages', body)
        
        clearLists(listName="today.txt")
        with open("tomorrow.txt", "r+") as f:
            tomorrow = f.read()
            with open("today.txt", "w") as d:
                d.write(tomorrow)
                clearLists(listName="tomorrow.txt")
                with open("after_tomorrow.txt", "r") as at:
                    with open("tomorrow.txt", "w") as tmr:
                        tmr.write(at.read())
                    clearLists(listName="after_tomorrow.txt")
        # Set new last report date
        lastReportDate(date=datetime.now().strftime('%Y, %m, %d'))
        #clearLists(listName='all')


#clearLists(listName='all')
lastReportDate(date='2020, 6, 23')
createWebhook(bearer, webhookUrl)

sched = BackgroundScheduler(daemon=True)
sched.add_job(editLists, 'interval', minutes=60)
sched.start()