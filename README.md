# Booking workplace solution Webex bot. How to use Adaptive card in Webex teams 

The Bot that can help to book and manage office workplace (given the limitations associated with COVID-19)

Booking workplace bot - the app that uses Webex Bot for manage and booking workplace in the office.

- [x] collect/count the user's workplace bookings on a certain date
- [x] count free workspace based on office capabilities (given the limitations associated with the pandemic)
- [x] aggregate and submit daily reports with information about bookings and available (empty) seats to Space(Room) (or user list)
- [x] sending information through Webex Teams

For which purpose you can use it:
- for manage workplaces
- booking workplace
- inform employees (using one simple command) about news, task, using Webex Teams direct message 

### Requirements
- [Python](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)

### How works with adaptive cards

#### Creating a webhooks 

For reading data from users after Adaptive Card interaction and sending messages we create two webhooks:

```
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
```

#### Creating and sending an Adaptive card 

For send adaptive card you need to use POST method

Sample of Python function

```
def postCard(personEmail):
    # open and read data from the file as part of the body for request
    with open("cardText.txt", "r", encoding="utf-8") as f:
        data = f.read().replace('USER_EMAIL', personEmail)
    # Add encoding, if you use non-Latin characters
    data = data.encode("utf-8")
    request = requests.post('https://webexapis.com/v1/messages', data=data, headers=headers).json()
```

<details><summary>Sample of body (click me)</summary>
<p>
{
    "toPersonEmail": "USER_EMAIL",
    "markdown": "Date for Booking",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.0",
                "body": [
                    {
                        "type": "Image",
                        "altText": "",
                        "url": "https://i.ibb.co/YLLVkVs/book-workplace.png"
                    },
                    {
                        "type": "TextBlock",
                        "text": "Select a date to book the workplace. If limit will be exceeded, you receive a corresponding message",
                        "wrap": true
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "Book for today",
                        "data": {
                            "button": "today"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "Book for tomorrow",
                        "data": {
                            "button": "tomorrow"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "Book for the day after tomorrow",
                        "data": {
                            "button": "after tomorrow"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "View free workplace",
                        "data": {
                            "button": "free space"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    }
                ]
            }
        }
    ]
}

</p>
</details>

#### How get data after users interacting with Adaptive card 

You can read users interaction like wich button pushed or data entered. 

After user interact with element like button with next parameters
```
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "Send data",
                        "data": {
                            "button": "send_inform"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    }
```

After pushing buton with type `Action.Submit` on your webhook server you recive `POST` request like below :

```
{
   "actorId":"Y2lzY29z...............L1BFT1BMRS85NjVlM...............TYtOTVlMi1hMDljYmFl...........",
   "appId":"Y2lzY29zcG......................xJQ0FUSU9OL0MzMmM4MD................ZjE2ZjIyOGRmNjI4YmJjYTQ5YmE1MmZlY2JiMmM3ZDUxNWNiNG.............",
   "created":"2020-08-18T14:59:23.500Z",
   "createdBy":"Y2lzY2..................T1BMRS8wOGQ0O..................DItOGIyOC0zNjMwYjA............",
   "data":{
      "created":"2020-08-18T15:25:33.316Z",
      "id":"Y2lzY29zcGF................VEFDSE1FTlRfQU...................QwLWUxNjctMTFlYS1iNTI5LWY1YWU................",
      "messageId":"Y2lzY29..............BR0UvZjQ0ZWYzM..............WFhY2EtNGZkMmFi..............",
      "personId":"Y2lzY.............zL1BFT1BMRS85NjVlMT................YtOTVlMi1hMDljYm..............",
      "roomId":"Y2lzY.............00vNDU1NDIxN2Yt...............Y2Q0NGUzYT...........",
      "type":"submit"
   },
   "event":"created",
   "id":"Y2lz...........PT0svMjNiNTc3MzQt...............DQtZWMyOWM4M.............",
   "name":"Card Report collab bot Webhook",
   "orgId":"Y2l............9SR0FOSVpBVElP.............LTQxN2YtOTk3NC1hZDcyY2F..........",
   "ownedBy":"creator",
   "resource":"attachmentActions",
   "status":"active",
   "targetUrl": "https://domain_for_webhook.com"
}  
```

For reading data, you need to filtered webhook as in the sample below, and get JSON data by webhook ID:

```
if webhook['resource'] == 'attachmentActions':
            result = send_webex_get('https://webexapis.com/v1/attachment/actions/{}'.format(webhook['data']['id']))
```            

In response, you can find key `"inputs"` where you can parse all inputs from the user  
```
{
   "id":"Y2lzY29zc.............VEFDSE1FTlRfQUNUSU9OLzBiMT..........QtMTFlYS05MzA3LTg3ZjgwOTQ........NQ",
   "type":"submit",
   "messageId":"Y2lzY29.........L01FU1NBR0UvZj..........E2My0xMWVhLTg3ODktY.....czNTl.....Rk",
   "inputs":{
      "button":"after tomorrow"
   },
   "personId":"Y2lzY29.........FT1BMRS85...VlMTM0MS1jMDQwL.........Mi1hMDljYmFlNTF....",
   "roomId":"Y2lzY29zcGFyazovL3VzL1JPT00vNDU1NDIxN2YtYzQwZS0zOGE2LWIxNTEtY2Q0NGUzYTRkZmE3",
   "created":"2020-08-18T15:03:58.730Z"
}
```
And here is the sample of response if you sent this card

![](img/Adaptive_card_with_buttons_and_text_fields.png)

<details><summary>this card (click)</summary>
<p>
{
    "toPersonEmail": "USER_EMAIL",
    "markdown": "Inform Card",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.0",
                "body": [
                    {
                        "type": "Image",
                        "altText": "",
                        "url": "https://i.ibb.co/YLLVkVs/book-workplace.png"
                    },
                    {
                        "type": "TextBlock",
                        "text": "Insert the text and image links in the appropriate fields below (you can use this resource https://imgbb.com/ after downloading select - HTML full linked, copy the URL from src = 'URL'",
                        "wrap": true
                    },
                    {
                        "type": "Input.Text",
                        "id": "Inform_text",
                        "placeholder": "Text to send (up to 2000 characters)",
                        "maxLength": 2000
                    },
                    {
                        "type": "Input.Text",
                        "id": "img_url",
                        "placeholder": "link to the image * .png, * .jpg"
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "Test",
                        "data": {
                            "button": "test_inform"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                        {
                        "type": "Action.Submit",
                        "title": "Send a message to all contacts in the cardText_Inform.txt file",
                        "data": {
                            "button": "send_inform"
                            }
                        }
                        ],
                    "horizontalAlignment": "Left",
                    "spacing": "None"
                    }
                ]
            }
        }
    ]
}
</p>
</details>

```
{

   "id": "Y2lzY29.......L0FUVEFDSE1FTl.........YjljYzQwLWUxN..........1iNTI5LWY1YWUzMGMy.......",
   "type": "submit",
   "messageId": "Y2lz...........01FU1NBR0........zAtZTE2Ni0xMWVhLWFh.......mFiODMw.....",
   "inputs": {
      "button": "send_inform",
      "Inform_text": "TEST TEXT",
      "img_url": "https://i.ibb.co/YLLVkVs/book-workplace.png"
   },

   "personId": "Y2l..........L1BFT1BMRS8........DQwLTQ4MTYtOTVlM.....ljYmFlNT......",
   "roomId": "Y2lzY29...........L1JPT00vNDU1NDIx.........zOGE2LWIxNTEtY2Q0NGUzYTR.....",
   "created": "2020-08-18T15:25:33.316Z"

}
```


Below you can see some example
You can test to send your using this project (paste your Adaptive Card Payload in this file [cardText.txt](cardText.txt)) or using this Postman collection

Useful links:
- [Adaptive buttons and cards designer](https://developer.webex.com/buttons-and-cards-designer)
- [Use Adaptive cards in Webex Teams](https://developer.webex.com/docs/api/guides/cards)
- [Docs and Schema Explorer](https://docs.microsoft.com/en-us/adaptive-cards/)

After sending you can get details using this request

And parse date from user

### Installation

**1. Clone and open project**

```
git clone https://github.com/oborys/booking_workplace_webex_bot
cd booking_workplace_webex_bot
```
**2. Open files [cred](cred), [app/views.py](app/views.py) and [Dockerfile](Dockerfile)**

**3. Create a Webex bot and Webhook**

Create Webex Bot:
- [Sign-up](https://www.webex.com/pricing/free-trial.html) or [Sign-in](https://teams.webex.com/signin) in Webex Teams
- Go to [https://developer.webex.com/](https://developer.webex.com/), then click [My Apps](https://developer.webex.com/my-apps) and click Create a Bot

Copy Bot's Access Token
![](img/App_Bot_Token.png)

**Paste it into the file [cred](cred) variable `WEBEX_TEAMS_TOKEN` and past bot email in `WEBEX_BOT_EMAIL` variable**

Create Team and Space where bot can publish dayli booking report

You can add the 'roomid@webex.bot' bot to the room and it will send you the roomId in a private message and then remove itself from the room

**Paste it into the file [cred](cred) variable `WEBEX_TEAMS_ROOM_ID_REPORT`**

For sent information to your server/localhost, create [Webhook](https://developer.cisco.com/learning/tracks/devnet-express-cloud-collab-it-pro/creating-spark-bots-itp/collab-spark-botl-itp/step/4)

For testing on localhost, you can use [ngrok](https://ngrok.com/download)
After installing ngrok open **new terminal window** and run the command
For fix [Webhook delivery issues with ngrok](https://developer.webex.com/blog/webhook-delivery-issues-with-ngrok)
```
ngrok http 56733
```
![](img/ngrok.png)

#### Do not close this terminal window, since the app needs it to redirect webhooks to your localhost.

**Сopy and paste url in file [app/views.py](app/views.py) variable `webhookUrl`**

Open file [employeesEmail.txt](employeesEmail.txt) and add emails of each employee whom you want to inform using '/inform' command.

Open file [app/views.py](app/views.py) and in this variable `adminEmailList` add email list of users/admins who can use the command `/inform` that can send information to employees

**4. Set daily report time**

In this file [cred](cred) you can set daily report time.
> For example if you set  this param as `REPORT_TIME = 20:00`
and run the app at 17:14 bot report will be sent at 20:14


**5. Set your time zone in [Dockerfile](Dockerfile)**

By default, timezone is Europe/Kyiv

**After completing all the above points, we can build a container**

Run docker container on port 56733
```
bash start.sh
```

Check app availability on your server http://ip-address:56733 or http://localhost:56733

For checking docker container you can use next CLI command

```
docker ps
```
![](img/docker_ps.png)

Running the next command you can see information about container logs, also monitor all output information from the Python app. And command like print, logging.debug, logging.info, logging.warning.   

```
docker logs [CONTAINER ID]
```
If you edit code files or requirements.txt, run next commands to apply changes
```
sudo docker stop sport_report_collab.docker && sudo docker start sport_report_collab.docker
```

Remove the docker container. In case if you got some critical errors, or edit your `Dockerfile` or `uwsgi.ini`
```
docker rm -f [CONTAINER ID]
```
### Interaction with bot

Find a bot to interact with

Enter the email of bot that you create

![](img/find_bot.png)


Interaction with bot

![](img/Webex_Adaptive_Card.png)

Sample of daily report

![](img/list_report_text.png)

### How it's works

The main part of the code is stored in `app/views.py`

Users can send message to the bot, bot reply with adaptive card:
![](img/Webex_Adaptive_Card.png)

After users books Get motivated response sentence like "Motivation to work is part of the motivation to live.".
this sentence stored in file:

`sentence_done.txt`

If user have already booked workplace for this date, users recive message `You have already booked a place earlier`

You can edit this file and add in there your custom responses.

> Each response should be in a new line. The code detects the Unix system's newlines (\n) symbol as a line delineator.

If the user book workplace on a certain day and capacity of this day is full users get a message `Sorry, all seats have already booked for this day. Try to choose another day, or booking a meeting room. In case of an emergency, contact the lobby.`

#### Available commands

**/inform**
In response to the message `/inform`, the bot sends such a card there are two fields in one, we insert the text into the other link to the picture. Then there are two "Test" buttons, after clicking this button - a message comes from bot to your 1-to-1 space and you can view how the text/picture is displayed. The second button “Send a message to all contacts in the file cardText_Inform.txt” sends a message to everyone)
> this command is available only for users wich emails is in variable adminEmailList (line 18, [this file](app/views.py))

**/list**
In response to the message `/list`, the bot sends a list of workplaces bookings on today, tomorrow and day after tomorrow

![](img/list_report_text.png)


At the end of source code, you can find a scheduler
```
sched = BackgroundScheduler(daemon=True)
sched.add_job(sendStatistic, 'interval', minutes=60)
sched.start()
```
When you want to quickly test and debug your changes you can change variable `minutes` from `60` to `1` minute.


**Other Useful links**

- [How To Build and Deploy a Flask Application Using Docker on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-18-04)
