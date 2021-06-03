import sys
import flask
import pymssql
import json
from flask import request, url_for
from flask_mail import Mail, Message


app = flask.Flask(__name__)
app.config.from_object('config')
mail = Mail(app)
stop_mail = False

def send_mail():
    global stop_mail
    if not stop_mail:
        msg = Message('Web service HappyPhone issue !', sender = 'backup@support.mba.be', recipients = ['vince.grad@gmail.com'])
        if sys.exc_info()[0]:
            msg.body = "There is the error from the web service: \n\r" + str(sys.exc_info()[0])
        else:
            msg.body = "There is an error with the service worker \n\r"
        mail.send(msg)
        stop_mail = True


@app.route('/', methods=['GET'])
def home():
    return "<p>You can use the url /api/callerid/<phone> to launch the procedure.</p>"
    
@app.route('/api/callerid/<phone>', methods=['GET'])
def get_phone(phone):
    SQL = "EXEC [dbo].[HappyPhone_Global_Search_For_Phone_Display] @numPhone='"

    if phone == None:
        return "Error: No phone number", 400

    if not phone.isdigit():
        return 'Error: This is not a phone number', 400

    try:
        connection = pymssql.connect(server=app.config.get('SERVER'), user=app.config.get('USERNAME'), password=app.config.get('PASSWORD'), database=app.config.get('DATABASE'))  
        cursor = connection.cursor()
        cursor.execute(SQL+phone+"'")
        rows = cursor.fetchall()
        print(rows[0][0])
        if rows[0][0] is None:
            return phone, 500
        return rows[0][0], 200
        
    except:
        global stop_mail
        print(sys.exc_info()[0])
        send_mail()
        
        return phone, 500

app.run()
