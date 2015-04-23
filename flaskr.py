from flask import Flask
from flask import g
from flask import jsonify
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
import queue
import os
import sqlite3
import pickle
import threading
from twython import Twython

basedir = os.path.abspath(os.path.dirname(__file__))

entryQueue = queue.Queue()
app = Flask(__name__)
app.debug = True

#app.config["MONGODB_SETTINGS"] = {'DB': "my_tumble_log"}
#app.config["SECRET_KEY"] = "KeepThisS3cr3t"

#db = MongoEngine(app)

@app.route('/')
def mainPage(entries=None):
    contacts = getEntries()
    return jsonify(contacts = contacts)

@app.route('/contacts/', methods=['GET', 'POST'])
def showContacts(entries=None):
    if request.method == 'POST':
        #for key in request.form:
            #entry = eval(key)
        
        newName = request.form['name']
        newLocation = request.form['location']
        newFollowers = request.form['followers']
        newTweets = reqeuest.form['tweets']
        newContact = createContact(newName,newLocation, newFollowers, newTweets)
        print(newContact)
        makeContact(newContact)
        return 'anything'

    if request.method == 'GET':
        entries= getEntries()
        return render_template('display.html', contacts = entries)
        # return jsonify(contacts =  entries)

@app.route('/update/')
def update():
    addTwitterEntries()
    return "It worked"

@app.route('/contacts/<contactid>', methods=['GET','PUT','DELETE'])
def contacts(contactid):
    if request.method == 'PUT':
        #for key in request.form:
            #entry = eval(key)
        newName = request.form['name']
        newLocation = request.form['location']
        newFollowers = request.form['followers']
        newTweets = request.form['tweets']
        newList = updateContact(contactid,newName,newLocation,newFollowers, newTweets)
        print(newList)
        saveEntries(newList)
        return 'something'

    if request.method == 'DELETE':
        newList = deleteContact(contactid)
        saveEntries(newList)
        return jsonify(contacts = newList)
    if request.method == 'GET':
        entries= getEntries()
        print(contactid)
        for entry in entries:
            print(entry['id'])
            if entry['id'] == int(contactid):
                print(entry)
                return jsonify(contact = entry)

@app.route('/delete/<contactid>')
def deleteSingleContact(contactid):
    newList = deleteContact(contactid)
    saveEntries(newList)
    return redirect(url_for('showContacts'))

@app.route('/contacts/create')
def createEntry():
    return render_template('create.html') 

@app.route('/contacts/created/',methods=['POST'])
def createdEntry():
    newName = request.form['name']
    newLocation = request.form['location']
    newFollowers = int(request.form['followers'])
    newTweets = int(request.form['tweets'])
    makeContact(createContact(newName, newLocation, newFollowers, newTweets))
    return(redirect(url_for('showContacts')))

@app.route('/contacts/update/<contactid>')
def updateEntry(contactid):
    theEntry = getContact(int(contactid))
    try:
        return render_template('update.html', entry= theEntry) 
    except:
        return "Item doesn't exist"

@app.route('/contacts/updated/',methods=['POST'])
def updatedEntry():
    contactid= request.form['id']
    newName = request.form['name']
    newLocation = request.form['location']
    newFollowers = int(request.form['followers'])
    newTweets = int(request.form['tweets'])
    newList = updateContact(contactid,newName,newLocation,newFollowers, newTweets)
    saveEntries(newList)
    return(redirect(url_for('showContacts'))) 

def createContact(name, location, followers, tweets):
    newContact = {}
    newContact['id'] = getNewID()
    newContact['name'] = name
    newContact['location'] = location
    newContact['followers'] = followers
    newContact['tweets'] = tweets
    return newContact

def updateContact(contactid, name, location, followers, tweets):
    entries = getEntries()
    for entry in entries:
        if entry['id'] == int(contactid):
            entry['name'] = name
            entry['location'] = location
            entry['followers'] = followers
            entry['tweets'] = tweets
    return entries

def deleteContact(contactid):
    return [x for x in getEntries() if x['id'] != int(contactid)]

def getContact(contactid):
    return [    item for item in getEntries() if item['id'] == int(contactid)][0]

def makeContact(newContact):
    if getEntries():
        newEntries = getEntries() + [newContact]
    else:
        newEntries = [newContact]
    saveEntries(newEntries)

    #infile =  open('contacts.txt',"r+") 
    #infile.seek(0)
    #infile.write(str(newEntries))
    
def getNewID():
    if getEntries():
        return getEntries()[-1]['id']+1
    else:
        return 0

def saveEntries(contacts):
    pickle.dump(contacts, open(app.config['PICKLE_PATH'], "wb"))

def getEntries():
    contacts = []
    if(os.path.getsize(app.config['PICKLE_PATH']) > 0):
        contacts = pickle.load(open(app.config['PICKLE_PATH'], "rb"))
    return contacts
    


def queryTwitter():
    # App key and secret found by registering Twitter App
    APPSECRET = "CPMs6yeXwWRqV5Yow7QmOVZzfouC2UOT1AIykCZKYwBzuUrw0b"
    APPKEY = 'ngJbJ1mb6uHR0oZvTO5QjPUtz'
    QUERY = "hello"
    twitter = Twython(APPKEY, APPSECRET)
    results = twitter.search(q=QUERY, lang='en', count= 100, result_type='popular')  # since_id =  currentID
    #pdb.set_trace() 
    resultsStatuses = {v['id']:v for v in results['statuses']}.values()
    # Threading is efficient because we're waiting on api requests 
    threads = [threading.Thread(target=resolveEntry, args=(entry,)) 
              for entry in resultsStatuses]  # Thread Pool Generator
    for thread in threads:
        thread.start()

    for thread in threads:
            thread.join()

    contactsToAdd=list()
    while(not entryQueue.empty()):
        contactsToAdd.append( entryQueue.get())

    return contactsToAdd

def addTwitterEntries():
    entries = queryTwitter()
    for entry in entries:
        makeContact( createContact( entry['name'],entry['location'], entry['followers'], entry['tweets']))


def resolveEntry(status):
    entryQueue.put( {"name":status['user']['name'], 'location':status['user']['location'], 'followers': status['user']['followers_count'], 'tweets':status['user']['statuses_count'] })

########## DB ##########
'''
class Post(db.Document):
    id = db.IntField(required=True)
    name = db.StringField(required=True)
    location = db.StringField(required=True)
    followers = db.IntField(required=True)
    tweets = db.IntField(required=True)
'''

if __name__ == '__main__':
    app.config.from_object('config.ProductionConfig')
    app.run()
