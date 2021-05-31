import sys
import flask
import pymssql
from flask import request, url_for
from flask_mail import Mail, Message


#Serveur config
HOST = "127.0.0.1"
PORT = 8000
#Database config
SERVER = "192.168.1.231\MBASQL16E"
DATABASE = "HappyPHone"
USERNAME = "DANIEL2020"
PASSWORD = "tvhcGi1dHCZKULYMHz+j4M7NgrM87Kqu+UutPPtQHvQ="
SQL = "EXEC [dbo].[HappyPhone_Global_Search_For_Phone_Display] @numPhone="


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'backup@support.mba.be'
app.config['MAIL_PASSWORD'] = 'Back.mba.1212'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
stop_mail = False


@app.route('/', methods=['GET'])
def home():
    return "<p>You can use the url /api/phone?phone=0475286111 to launch the procedure.</p>"
    
@app.route('/api/callerid/<phone>', methods=['GET'])
def get_phone(phone):
    #phone = request.args.get("phone")

    if phone == None:
        return "Error: No phone number", 400

    if not phone.isdigit():
        return 'Error: This is not a phone number', 400

    try:
        connection = pymssql.connect(server=SERVER, user=USERNAME, password=PASSWORD, database=DATABASE)  
        cursor = connection.cursor()
        cursor.execute(SQL+phone)
        rows = cursor.fetchall()
        return rows[0][0], 200
    except:
        global stop_mail
        if not stop_mail:
            msg = Message('Web service HappyPhone issue !', sender = 'backup@support.mba.be', recipients = ['vince.grad@gmail.com'])
            if sys.exc_info()[0]:
                msg.body = "There is the error from the web service: \n\r" + str(sys.exc_info()[0])
            else:
                msg.body = "There is an error with the service worker \n\r"
            mail.send(msg)
            stop_mail = True

        return phone, 500

app.run(host = HOST, port = PORT)