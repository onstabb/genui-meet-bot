import os
TOKEN = os.environ.get('TOKEN') 
USER_AGENT = os.environ.get('USER_AGENT')
URL = os.environ.get('DATABASE_URL') 
URI = os.environ.get('MONGODB_URI') 

admins = {"main": 1}


class Mongo:
    link = URI[10:]
    username = link.split(':')[0]
    password = link.split(":")[1].split('@')[0]
    host = link.split('@')[1].split(':')[0]
    port = link.split(":")[2].split('/')[0]
    db_name = link.split('/')[1]
