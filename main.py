#Personal Assistant - a text based personal assistant.
# Dylan Bowman 2017
# Version 0.1

#Local imports
import emailLib, weather, news, calendarLib, reminders, disneyland, reddit, traffic
#Python imports
import configparser, time, traceback

def main():
    config=configparser.ConfigParser()
    config.read("config.ini")
    try:
        authorized = config["email"]["authorized"].replace(" ","").split(",")
    except:
        print("There was an issue with your authorized email addresses. Is your configuration set up properly?")
        quit()
    admin = [config["email"]["admin"]]
    try:
        digest = time.strptime(config["email"]["digest"],"%I:%M %p")
    except:
        print("Couldn't understand your digest time. Assuming digest time to be now.")
        digest = time.localtime()


    #dailyDigest(config)
    send_text(config,admin,"System is up and running.")
    print("System is up and running.")
    lastDaily = 0 #Last day daily digest was sent (so it only sends 1)
    run_app = True # Change this to false to quit the application.
    lastMinute = -1
    while(run_app):
        #Check if it's time to run a digest.
        lt = time.localtime()
        if lt[3] == digest[3] and lt[4] == digest[4] and lastDaily != lt[7]:
            lastDaily = lt[7]
            dailyDigest(config)
        #Read emails and respond if needed.
        try:
            messages = read_emails(config)
            if messages != False:
                for message in messages:
                    if message[0] in authorized:
                        run_app = process_message(message,config)
                    else:
                        print("Unauthorized user sending mail: "+message[0])
        except:
            print("Couldn't read emails.")
            traceback.print_exc()
        #Check for any reminders that need to be sent every minute.
        if lastMinute != lt[4]:
            r = reminders.Reminders()
            r.parseCSV("reminders.csv")
            text = r.getTimeReminders()
            if text != "":
                send_text(config,config["email"]["admin"],"Reminder: "+text)
            r.writeCSV("reminders.csv")
        time.sleep(1)

def process_message(message,config):
    message_body = message[1].lower().replace("\n","")
    split_msg = message_body.split(" ")
    print("User: "+message_body)
    #Determine where to send the reply.
    reply = message[0]
    if config["email"]["singleReply"].lower() == "yes":
        reply = [config["email"]["admin"]]


    if message_body == "quit":
        print("Recieved quit command. Exiting.")
        send_text(config,reply,"Goodbye.")
        return False
    elif message_body == "time" or message_body=="date":
        print("Sent date to user.")
        send_text(config,reply,time_date())
        return True
    elif split_msg[0]=="weather":
        ## If the user input a weather command, send it to the weather module.
        out = weather.readInput(message_body,config)
        print("Me: "+out)
        send_text(config,reply,out)
        return True
    elif split_msg[0] == "news":
        ## If the user input a news command, send it to the news module.
        out = news.readInput(message_body,config)
        print("Me: "+out)
        send_text(config,reply,out)
        return True
    elif split_msg[0] == "calendar":
        out = calendarLib.readInput(message_body,config)
        print("Me: "+out)
        send_text(config,reply,out)
        return True
    elif split_msg[0] == "reminders":
        r = reminders.Reminders()
        r.parseCSV("reminders.csv")
        out = r.readInput(message_body)
        if out != True:
            print("Me: "+out)
            send_text(config,reply,out)
        else:
            print("No need to reply.")
        r.writeCSV("reminders.csv")
        return True
    elif split_msg[0] == "disneyland":
        out=disneyland.read_input(message_body,config)
        print("Me: "+out)
        send_text(config, reply,out)
        return True
    elif split_msg[0] == "reddit":
        out=reddit.readInput(config,message_body)
        print("Me: "+out["title"])
        t = "Top post on /r/"+out["sub"]+": "+out["title"]
        if out["is_photo"]:
            send_attachment(config,reply,t,out["location"])
        else:
            send_text(config,reply,t+" @ "+out["url"])
        return True
    elif split_msg[0] == "traffic":
        out = traffic.read_input(message_body,config);
        print("Me: "+out)
        send_text(config, reply, out)
        return True
    else:
        print("Couldn't understand message: "+message_body)
        return True

def dailyDigest(config):
    print("Sending daily digest.")
    to = config["email"]["admin"]
    #Get the date.
    lt = time.localtime()
    d = date()
    #Get the weather.
    location = config["Weather"]["default_location"]
    json_data = weather.get_weather(location)
    forecast = weather.digestable(json_data)
    #Get upcoming calendar events, if there are any.
    events = ""
    upcoming = calendarLib.getUpcomingEvents(config["calendar"]["url"],config["calendar"]["timezone"])
    for event in upcoming:
        if event.date[0] == lt[0] and event.date[1]==lt[1] and event.date[2]==lt[2]:
            events += event.prettyPrint(False)+"\n"
    if events != "":
        events = "Today's events: \n"+events
    else:
        events = "You have no events today!\n"
    output = "Good morning! It is "+d+". "+forecast+"\n"+events +"Hope you have a great day!"
    print("Sending: ")
    print(output)
    send_text(config,to,output)
    print("Getting top reddit post.")
    d = reddit.digestable(config)
    print("Sending: "+d["title"])
    t = "Top post on /r/"+config["reddit"]["sub"]+": "+d["title"]
    if d["is_photo"]:
        send_attachment(config,to,t,d["location"])
    else:
        send_text(config,to,t+" @ "+d["url"])

def date():
    # Returns a nice-looking date.
    lt = time.localtime()
    suffix = "th"
    if lt[2]%10==1:
        suffix = "st"
    elif lt[2]%10==2:
        suffix = "nd"
    elif lt[2]%10==3:
        suffix = "rd"
    number = str(lt[2])
    return time.strftime("%A, %B "+number+suffix,lt)

def time_date():
    # Returns a nice-looking time/date.
    lt = time.localtime()
    suffix = "th"
    if lt[2]%10==1:
        suffix = "st"
    elif lt[2]%10==2:
        suffix = "nd"
    elif lt[2]%10==3:
        suffix = "rd"
    number = str(lt[2])
    return time.strftime("%A, %B "+number+suffix+", %Y %I:%M:%S %p", time.localtime())

def read_emails(config):
    user = config["email"]["user"]
    password = config["email"]["password"]
    imap_addr = config["email"]["imap_server"]
    return emailLib.read_email(user,password,imap_addr)

def send_text(config,to,body):
    user = config["email"]["user"]
    password = config["email"]["password"]
    smtp_addr = config["email"]["smtp_server"]
    emailLib.send_email(user,password,to,"",body,smtp_addr)

def send_attachment(config,to,body,file):
    user = config["email"]["user"]
    password = config["email"]["password"]
    smtp_addr = config["email"]["smtp_server"]
    emailLib.send_attachment(user,password,to,"",body,file,smtp_addr)


if __name__ == "__main__":
    main()
