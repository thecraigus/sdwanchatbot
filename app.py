from flask import Flask, request
import requests

from webexteamssdk import WebexTeamsAPI, Webhook
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Module constants
CAT_FACTS_URL = 'https://catfact.ninja/fact'



app = Flask(__name__)

api = WebexTeamsAPI()


def get_catfact():
    """Get a cat fact from catfact.ninja and return it as a string.
    Functions for Soundhound, Google, IBM Watson, or other APIs can be added
    to create the desired functionality into this bot.
    """
    response = requests.get(CAT_FACTS_URL, verify=False)
    response.raise_for_status()
    json_data = response.json()
    return json_data['fact']


# Core bot functionality
# Your Webex Teams webhook should point to http://<serverip>:5000/events
@app.route('/events', methods=['GET', 'POST'])
def webex_teams_webhook_events():
    """Processes incoming requests to the '/events' URI."""
    if request.method == 'GET':
        return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Teams Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>Your Flask web server is up and running!</strong>
                   </p>
                   <p>
                   Here is a nice Cat Fact for you:
                   </p>
                   <blockquote>{}</blockquote>
                   </body>
                   </html>
                """.format(get_catfact()))
    elif request.method == 'POST':
        json_data = request.json
        print("\n")
        print("WEBHOOK POST RECEIVED:")
        print(json_data)
        print("\n")

        # Create a Webhook object from the JSON data
        webhook_obj = Webhook(json_data)
        # Get the room details
        room = api.rooms.get(webhook_obj.data.roomId)
        # Get the message details
        message = api.messages.get(webhook_obj.data.id)
        # Get the sender's details
        person = api.people.get(message.personId)

        print("NEW MESSAGE IN ROOM '{}'".format(room.title))
        print("FROM '{}'".format(person.displayName))
        print("MESSAGE '{}'\n".format(message.text))

        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        me = api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            return 'OK'

        else:
            # Message was sent by someone else; parse message and respond.
            if "/CAT" in message.text:
                username = 'devnetuser'
                password = 'RG!_Yw919_83'
                vManage = 'sandbox-sdwan-1.cisco.com'
                authurl = 'https://{}/j_security_check'.format(vManage)
                authbody = {'j_username': f'{username}', 'j_password': f'{password}'}
                headers = {'content-type': 'application/json', 'accept': 'application/json'}
                url = f'https://{vManage}/dataservice/'
                token_url = url + 'client/token'

                viptella = requests.session()
                authenticate = viptella.post(url=authurl, data=authbody, verify=False)

                login_token = viptella.get(url=token_url, verify=False)

                viptella.headers['X-XSRF-TOKEN'] = login_token.content


                getEvents = viptella.get(url=f"https://{vManage}:443/dataservice/device/monitor", verify=False).json()

                deviceStatus = []
                for device in getEvents['data']:
                    deviceStatus.append(device['host-name']+f' Status: {device["status"]}')
                api.messages.create(room.id, text=str(deviceStatus))
            return 'OK'



#         return str(deviceStatus)

if __name__ == '__main__':
    # Start the Flask web server
    app.run()
