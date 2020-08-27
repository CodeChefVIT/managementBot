

import discord
from discord.ext import commands
from botpass import *
import os
import smtplib
import psycopg2
from datetime import date

EMAIL_ADDRESS = userid
EMAIL_PASSWORD = userpass

conn = psycopg2.connect(database = "managementbot", user = "postgres", password = "1234", host = "127.0.0.1", port = "5432")
print ("Opened database successfully")

cur = conn.cursor()

cur.execute('''CREATE TABLE DISCORDBOT
      (SERVER           VARCHAR(50)    NOT NULL,
      CHANNEL           VARCHAR(50)    NOT NULL,
      USERNAME            VARCHAR(50)     NOT NULL,
      MSGCNT        INT,
      EMAIL         TEXT);''')

conn.commit()

cur.execute('''CREATE TABLE MESSAGES
      (SERVER           VARCHAR(50)    NOT NULL,
      CHANNEL           VARCHAR(50)    NOT NULL,
      MSGID            VARCHAR(50)     NOT NULL,
      DATE        TEXT,
      ROLES         VARCHAR(200));''')

conn.commit()

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):

    id = client.get_guild(729892665390268467)

    if "BOT" in str(message.author.name):
        pass
    elif "GitHub" in str(message.author.name):
        pass
    else:
        role_str=[]
        role=message.author.roles
        for i in role:
            role_str.append(str(i.name))
        if(len(role_str)):
            cur.execute("INSERT INTO MESSAGES (server,channel,MSGID,DATE,ROLES) VALUES (%s,%s,%s,%s,%s)", (str(message.guild),str(message.channel.name), str(message.id), str(date.today()), str("!.#$%".join(role_str))))

    # Counts the number of messages by each member
    if "BOT" in str(message.author.name):
        pass
    elif "GitHub" in str(message.author.name):
        pass
    else:
        
        cur.execute("SELECT channel, username, msgcnt, email from DISCORDBOT where server='%s'" % (str(message.guild)))
        rows = cur.fetchall()
        if(len(rows)):
            flag=0
            for row in rows:
                if(row[0]==message.channel.name and row[1]==message.author.name):
                    flag=1
                    cur.execute("UPDATE DISCORDBOT set MSGCNT = %s where CHANNEL = %s and USERNAME = %s and SERVER = %s", (int(int(row[2])+1), str(message.channel.name), str(message.author.name),str(message.guild)))
                    break
            if(flag==0):    
                cur.execute("INSERT INTO DISCORDBOT (server,channel,USERNAME,MSGCNT,EMAIL) VALUES (%s,%s,%s,1,'Not Updated')", (str(message.guild),str(message.channel.name), str(message.author.name)))
        
        else:
            cur.execute("INSERT INTO DISCORDBOT (server,channel,USERNAME,MSGCNT,EMAIL) VALUES (%s,%s,%s,1,'Not Updated')", (str(message.guild),str(message.channel.name), str(message.author.name)))
        conn.commit()

    if message.content == "!users":                 # To find number of users in the channel 
        await message.channel.send(f"# of Members: {id.member_count}")

    elif message.content == "!msgcnt":              # To find number of messages sent by each users
        cur.execute("SELECT username, msgcnt from DISCORDBOT where channel = '%s' and server = '%s' " % (str(message.channel.name),str(message.guild)))
        rows = cur.fetchall()
        for i in rows:
            await message.channel.send(f"{i[0]}: {i[1]}")

    elif message.content == "!rstcnt":             # To reset the count of messages of each user in a channel
        cur.execute("DELETE from DISCORDBOT where CHANNEL = '%s' and server = '%s' " % (str(message.channel.name),str(message.guild)))
        conn.commit()

    elif str(message.content)[:9] == "!del role":  # Delete messages by the roles
        role_del = str(message.content)[9:]
        role_del = role_del.strip()
        cur.execute("SELECT channel, msgid, date, roles from MESSAGES where channel='%s' and server='%s' " % (str(message.channel.name),str(message.guild)))
        rows = cur.fetchall()
        for row in rows:
            list_split=str(row[3]).split("!.#$%")
            if str(role_del) in list_split:
                messages=await message.channel.fetch_message(int(row[1]))
                await messages.delete(delay=None)
                cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild),str(message.channel.name)))
                conn.commit()


    elif str(message.content)[:4] == "!del":      # To delete messages
        cur.execute("SELECT channel, msgid, date from MESSAGES where channel='%s' and server = '%s' " % (str(message.channel.name),str(message.guild)))
        rows = cur.fetchall()
        a=9999
        b=9999
        c=9999
        for i in rows:
            d=i[2]
            a1,b1,c1=str(d).split("-")
            a1=int(a1)
            b1=int(b1)
            c1=int(c1)
            if(a>a1):
                a=a1
                b=b1
                c=c1
            elif(a==a1):
                if(b>b1):
                    b=b1
                    c=c1
                elif(b==b1):
                    if(c>c1):
                        c=c1

        if str(message.content)[5:] == "week":   # To delete messages in the starting week
            for row in rows:
                d=row[2]
                a1,b1,c1=str(d).split("-")
                a1=int(a1)
                b1=int(b1)
                c1=int(c1)
                if(0<=c and c<=7):
                    if(a1==a and b1==b and 0<=c1 and c1<=7):
                        messages=await message.channel.fetch_message(int(row[1]))
                        await messages.delete(delay=None)
                        cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild),str(message.channel.name)))
                        conn.commit()

                elif(8<=c and c<=14):
                    if(a1==a and b1==b and 8<=c1 and c1<=14):
                        messages=await message.channel.fetch_message(int(row[1]))
                        await messages.delete(delay=None)
                        cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild),str(message.channel.name)))
                        conn.commit()

                elif(15<=c and c<=21):
                    if(a1==a and b1==b and 15<=c1 and c1<=21):
                        messages=await message.channel.fetch_message(int(row[1]))
                        await messages.delete(delay=None)
                        cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild),str(message.channel.name)))
                        conn.commit()

                elif(22<=c and c<=31):
                    if(a1==a and b1==b and 22<=c1 and c1<=31):
                        messages=await message.channel.fetch_message(int(row[1]))
                        await messages.delete(delay=None)
                        cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild),str(message.channel.name)))
                        conn.commit()

        elif str(message.content)[5:] == "month":     # To delete messages in the starting month
            for row in rows:
                d=row[2]
                a1,b1,c1=str(d).split("-")
                a1=int(a1)
                b1=int(b1)
                c1=int(c1)
                if(a1==a and b1==b):
                    messages=await message.channel.fetch_message(int(row[1]))
                    await messages.delete(delay=None)
                    cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild),str(message.channel.name)))
                    conn.commit()

    elif str(message.content[:6]) == "!email":       # Add the emails of the members
        email_add=message.content[6:]
        email_add=email_add.strip()
        cur.execute("UPDATE DISCORDBOT set EMAIL = '%s' where channel = '%s' and username = '%s' and server = '%s' " % (str(email_add), str(message.channel.name), str(message.author.name),str(message.guild)))
        conn.commit()


    elif message.content == "!help":                 # To show all the possible options available with the bot
        embed = discord.Embed(title="Help on BOT", description="Some useful commands")
        embed.add_field(name="!users",value="Returns the number of users in the channel")
        embed.add_field(name="!email <email id>",value="Sends an email when a pull request is made")
        embed.add_field(name="!del role <name of role>",value="Deletes the messages by members of the specified role")
        embed.add_field(name="!del week",value="Deletes the messages in the starting week")
        embed.add_field(name="!del month",value="Deletes the messages in the starting month")
        embed.add_field(name="!msgcnt",value="Returns the number of messages sent by each user")
        embed.add_field(name="!rstcnt",value="Resets the number of messages of each user to Zero")
        await message.channel.send(content=None, embed=embed)


    elif "GitHub" in str(message.author.name):      #To send emails when a Github Pull request is made

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            subject = "An update was made to the git repository"
            body = "An update was made to the git repository\n\n"

            for i in message.embeds:
                body+=i.title+"\n\n"
                body+=i.description+"\n\n\n\n"

            msg = f"Subject: {subject}\n\n{body}"

            cur.execute("SELECT email from DISCORDBOT where channel='%s' and server='%s'" % (str(message.channel.name),str(message.guild)))
            rows = cur.fetchall()
            for i in rows:
                if(i[0]!="Not Updated"):
                    smtp.sendmail(EMAIL_ADDRESS,i[0],msg)



@client.event
async def on_member_remove(member):

    # To remove the member from the database
    var_a=str(member.name)
    cur.execute("DELETE from DISCORDBOT where USERNAME='%s' and server='%s';" % (str(member.name),str(message.guild)))
    conn.commit()


client.run(token)