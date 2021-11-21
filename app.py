from flask import Flask, request
import requests
from webexteamssdk import WebexTeamsAPI, Webhook
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


username = 'devnetuser'
password = 'RG!_Yw919_83'
vManage = 'sandbox-sdwan-1.cisco.com'
authurl = 'https://{}/j_security_check'.format(vManage)
authbody = {'j_username': f'{username}', 'j_password': f'{password}'}
url = f'https://{vManage}/dataservice/'
token_url = url + 'client/token'

app = Flask(__name__)
api = WebexTeamsAPI()


@app.route('/events', methods=['GET', 'POST'])
def webex_teams_webhook_events():
    if request.method == 'GET':
        return ("""
                   <html>
                       <head>
                           <title>SDWAN Chatbot!</title>
                       </head>
                   <body>
                   <p>
                   <h1>SDWAN Chatbot</h1>
                   <h2>The App is running!</h2> 
                   </p>
                   </body>
                   </html>
                """)

    elif request.method == 'POST':
        json_data = request.json
        print('\n webhook data \n')
        print(json_data)

        webhook_data = Webhook(json_data)
        room = api.rooms.get(webhook_data.data.roomId)
        message = api.messages.get(webhook_data.data.id)


        bot = api.people.me()

        if message.personId == bot.id:
            return 'OK'

        else:
            if "sdwan controller status" in message.text:
                viptela = requests.session()
                viptela.post(url=authurl, data=authbody, verify=False)
                login_token = viptela.get(url=token_url, verify=False)
                viptela.headers['X-XSRF-TOKEN'] = login_token.content
                getStatus = viptela.get(
                    url=f"https://{vManage}:443/dataservice/device/monitor", verify=False).json()

                deviceStatus = []
                for device in getStatus['data']:
                    deviceStatus.append(
                        device['host-name']+f' Status: {device["status"]}')
                api.messages.create(room.id, text=str(deviceStatus))
            return 'OK'


if __name__ == '__main__':
    app.run()
