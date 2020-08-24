import os
TOKEN = os.environ.get('TOKEN') if os.environ.get('TOKEN') is not None else '1198394902:AAFSbNt4G8hR40XSdJsFrB03k14inEA1_5g'
USER_AGENT = os.environ.get('USER_AGENT') if os.environ.get('USER_AGENT') is not None else 'GenuiMeetBot'
URL = os.environ.get('DATABASE_URL') if os.environ.get('DATABASE_URL') is not None else "postgres://postgres:12345@localhost:5432/postgres"
URI = os.environ.get('MONGODB_URI') if os.environ.get('MONGODB_URI') is not None else 'mongodb://heroku_jchdx9gk:j8k71nvnmtpeb80t935q596org@ds221339.mlab.com:21339/heroku_jchdx9gk'

admins = {"main": 182694754}


class Mongo:
    link = URI[10:]
    username = link.split(':')[0]
    password = link.split(":")[1].split('@')[0]
    host = link.split('@')[1].split(':')[0]
    port = link.split(":")[2].split('/')[0]
    db_name = link.split('/')[1]