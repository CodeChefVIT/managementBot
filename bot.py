

import discord
from discord.ext import commands
import os
import smtplib
import psycopg2
from datetime import date
from mask import encrypt_string,decrypt_string
from decouple import config

EMAIL_ADDRESS = config('userid')
EMAIL_PASSWORD = config('userpass')

try:
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()

    cur = conn.cursor()

    cur.execute('''CREATE TABLE DISCORDBOT
        (SERVER           VARCHAR(100)    NOT NULL,
        CHANNEL           VARCHAR(100)    NOT NULL,
        USERNAME           VARCHAR(50)     NOT NULL,
        USERID             VARCHAR(50)     NOT NULL,
        MSGCNT        INT,
        EMAIL         TEXT,
        DATE        TEXT,
        ROLES         VARCHAR(200));''')

    conn.commit()

    cur.execute('''CREATE TABLE MESSAGES
        (SERVER           VARCHAR(100)    NOT NULL,
        CHANNEL           VARCHAR(100)    NOT NULL,
        MSGID            VARCHAR(50)     NOT NULL,
        DATE        TEXT,
        ROLES         VARCHAR(200));''')

    conn.commit()
    cur.close()
    conn.close()
except:
    pass

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):

    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    role_str=[]
    role=[]
    try:
        role=message.author.roles
    except:
        pass
    for i in role:
        role_str.append(str(i.name))
    if(len(role_str)):
        cur.execute("INSERT INTO MESSAGES (server,channel,MSGID,DATE,ROLES) VALUES (%s,%s,%s,%s,%s)", (str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id), str(encrypt_string(str(message.id))), str(date.today()), str("!.#$%".join(role_str))))
        print("(server,channel,MSGID,DATE,ROLES) inserted in messages table")
        conn.commit()

    # Counts the number of messages by each member
    if message.author.bot:
        pass
    else:
        role_str=[]
        role=message.author.roles
        for i in role:
            role_str.append(str(i.name))
        cur.execute("SELECT channel, username, msgcnt, email, userid from DISCORDBOT where server='%s'" % (str(message.guild)+str(message.guild.id)))
        rows = cur.fetchall()
        if(len(rows)):
            flag=0
            for row in rows:
                if(row[0]==str(message.channel.name)+str(message.channel.id) and row[1]==message.author.name and row[4]==str(message.author.id)):
                    flag=1
                    print(message.author.name,message.channel.name,int(row[2])+1,date.today())
                    cur.execute("UPDATE DISCORDBOT set MSGCNT = %s, ROLES = %s where CHANNEL = %s and USERNAME = %s and SERVER = %s and USERID = %s", (int(int(row[2])+1), str("!.#$%".join(role_str)), str(message.channel.name)+str(message.channel.id), str(message.author.name),str(message.guild)+str(message.guild.id), str(message.author.id)))
                    print(message.author.name,message.channel.name,int(row[2])+1,date.today())
                    conn.commit()
                    print("Updated Discord bot table")
                    break
            if(flag==0):    
                cur.execute("INSERT INTO DISCORDBOT (server,channel,USERNAME,USERID,MSGCNT,EMAIL,DATE,ROLES) VALUES (%s,%s,%s,%s,1,'Not Updated',%s,%s)", (str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id), str(message.author.name), str(message.author.id), str(date.today()), str("!.#$%".join(role_str))))
                print("(server,channel,USERNAME,MSGCNT,EMAIL,DATE,ROLES) inserted in DISCORDBOT table")
        
        else:
            cur.execute("INSERT INTO DISCORDBOT (server,channel,USERNAME,USERID,MSGCNT,EMAIL,DATE,ROLES) VALUES (%s,%s,%s,%s,1,'Not Updated',%s,%s)", (str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id), str(message.author.name), str(message.author.id), str(date.today()), str("!.#$%".join(role_str))))
            print("(server,channel,USERNAME,MSGCNT,EMAIL,DATE,ROLES) inserted in DISCORDBOT table")
        conn.commit()
        print("Saved to DB")


    if message.content == "!users":                 # To find number of users in the channel 
        await message.channel.send(f"# of Members: {message.guild.member_count}")


    elif message.content == "!msgcnt":              # To find number of messages sent by each users
        cur.execute("SELECT username, msgcnt, date from DISCORDBOT where channel = '%s' and server = '%s' " % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
        rows = cur.fetchall()
        for i in rows:
            await message.channel.send(f"{i[0]}: {i[1]}, Last msg posted on {i[2]}")

    elif str(message.content)[:7] == "!msgcnt":
        username = message.mentions
        for j in range(len(username)):
            cur.execute("SELECT username, msgcnt, date from DISCORDBOT where channel = '%s' and server = '%s' and username = '%s' and userid = '%s'" % (str(message.channel.name)+str(message.channel.id), str(message.guild)+str(message.guild.id), str(username[j].name), str(username[j].id)))
            rows = cur.fetchall()
            for i in rows:
                await message.channel.send(f"{i[0]}: {i[1]}, Last msg posted on {i[2]}")
            if(len(rows)==0):
                await message.channel.send(f"{username[j].name}: 0, No messages made")


    elif message.content == "!rstcnt":             # To reset the count of messages of each user in a channel
        cur.execute("DELETE from DISCORDBOT where CHANNEL = '%s' and server = '%s' " % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
        await message.channel.send(f"Message count for this whole channel has been reset ")
        print("A whole channel deleted in DISCORDBOT table")
        conn.commit()

    elif str(message.content)[:7] == "!rstcnt":      # To reset the count of messages of for the specified role in a channel
        role=message.role_mentions
        cur.execute("SELECT username, msgcnt, date, userid, roles from DISCORDBOT where channel = '%s' and server = '%s' " % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
        rows = cur.fetchall()
        for i in rows:
            for j in role:
                list_split=str(i[-1]).split("!.#$%")
                if(str(j.name) in list_split):
                    cur.execute("DELETE from DISCORDBOT where channel = '%s' and server = '%s' and username='%s' and date='%s' and roles='%s'" % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id),str(i[0]),str(i[2]),str(i[-1])))
                    print("Rows containing a specific role deleted in DISCORDBOT table")
                    conn.commit()
        if(len(role)):
            await message.channel.send(f"Message count for the roles mentioned in this channel has been reset ")

        username=message.mentions
        for j in range(len(username)):
            cur.execute("DELETE from DISCORDBOT where CHANNEL = '%s' and server = '%s' and username = '%s' and userid = '%s'" % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id), str(username[j].name), str(username[j].id)))
            print("Row containing a specific user deleted in DISCORDBOT table")
            conn.commit()
        if(len(username)):
            await message.channel.send(f"Message count for the usernames mentioned in this channel has been reset ")


    elif str(message.content) == "!del week":      # To delete messages in the starting week
        cur.execute("SELECT channel, msgid, date from MESSAGES where channel='%s' and server = '%s' " % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
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

        for row in rows:
            d=row[2]
            a1,b1,c1=str(d).split("-")
            a1=int(a1)
            b1=int(b1)
            c1=int(c1)
            if(0<=c and c<=7):
                if(a1==a and b1==b and 0<=c1 and c1<=7):
                    messages=await message.channel.fetch_message(int(decrypt_string(str(row[1]))))
                    await messages.delete(delay=None)
                    cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id)))
                    print("Rows with messages for a week deleted in MESSAGES table")
                    conn.commit()

            elif(8<=c and c<=14):
                if(a1==a and b1==b and 8<=c1 and c1<=14):
                    messages=await message.channel.fetch_message(int(decrypt_string(str(row[1]))))
                    await messages.delete(delay=None)
                    cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id)))
                    print("Rows with messages for a week deleted in MESSAGES table")
                    conn.commit()

            elif(15<=c and c<=21):
                if(a1==a and b1==b and 15<=c1 and c1<=21):
                    messages=await message.channel.fetch_message(int(decrypt_string(str(row[1]))))
                    await messages.delete(delay=None)
                    cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id)))
                    print("Rows with messages for a week deleted in MESSAGES table")
                    conn.commit()

            elif(22<=c and c<=31):
                if(a1==a and b1==b and 22<=c1 and c1<=31):
                    messages=await message.channel.fetch_message(int(decrypt_string(str(row[1]))))
                    await messages.delete(delay=None)
                    cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id)))
                    print("Rows with messages for a week deleted in MESSAGES table")
                    conn.commit()
        await message.channel.send(f"Messages for the first week in this channel has been deleted")

    elif str(message.content) == "!del month":      # To delete messages in the starting month
        cur.execute("SELECT channel, msgid, date from MESSAGES where channel='%s' and server = '%s' " % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
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

        for row in rows:
            d=row[2]
            a1,b1,c1=str(d).split("-")
            a1=int(a1)
            b1=int(b1)
            c1=int(c1)
            if(a1==a and b1==b):
                messages=await message.channel.fetch_message(int(decrypt_string(str(row[1]))))
                await messages.delete(delay=None)
                cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id)))
                print("Rows with messages for a month deleted in MESSAGES table")
                conn.commit()
        await message.channel.send(f"Messages for the first month in this channel has been deleted")

    elif str(message.content)[:4] == "!del":  # Delete messages by the roles
        role_del = message.role_mentions
        print(role_del)
        cur.execute("SELECT channel, msgid, date, roles from MESSAGES where channel='%s' and server='%s' " % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
        rows = cur.fetchall()
        for row in rows:
            for j in role_del:
                list_split=str(row[3]).split("!.#$%")
                if str(j.name) in list_split:
                    messages=await message.channel.fetch_message(int(decrypt_string(str(row[1]))))
                    await messages.delete(delay=None)
                    cur.execute("DELETE from MESSAGES where MSGID='%s' and server = '%s' and channel = '%s' ;" % (row[1],str(message.guild)+str(message.guild.id),str(message.channel.name)+str(message.channel.id)))
                    print("Rows with messages from a role deleted in MESSAGES table")
                    conn.commit()
        if(len(role_del)):
            await message.channel.send(f"Message made by users having the mentioned roles in this channel has been deleted ")


    elif str(message.content[:6]) == "!email":       # Add the emails of the members
        email_add=message.content[6:]
        email_add=email_add.strip()
        cur.execute("UPDATE DISCORDBOT set EMAIL = '%s' where channel = '%s' and username = '%s' and server = '%s' and userid = '%s'" % (str(email_add), str(message.channel.name)+str(message.channel.id), str(message.author.name),str(message.guild)+str(message.guild.id), str(message.author.id)))
        print("Email of a person updated in DISCORDBOT table")
        await message.channel.send(f"Email for the user {message.author.name} has been added in this channel")
        conn.commit()


    elif message.content == "!help":                 # To show all the possible options available with the bot
        embed = discord.Embed(title="Help on BOT", description="Some useful commands")
        embed.add_field(name="!users",value="Returns the number of users in the channel")
        embed.add_field(name="!email <email id>",value="Sends an email when a pull request is made")
        embed.add_field(name="!del <tag the roles>",value="Deletes the messages by members of the tagged roles")
        embed.add_field(name="!del week",value="Deletes the messages in the starting week")
        embed.add_field(name="!del month",value="Deletes the messages in the starting month")
        embed.add_field(name="!msgcnt",value="Returns the number of messages sent by each user")
        embed.add_field(name="!msgcnt <tag the users>",value="Returns the number of messages sent by the tagged users")
        embed.add_field(name="!rstcnt",value="Resets the number of messages of each user to Zero")
        embed.add_field(name="!rstcnt <tag the roles>",value="Resets the number of messages of each user of the tagged roles to Zero")
        embed.add_field(name="!rstcnt <name of the user>",value="Resets the number of messages of the tagged users to Zero")
        embed.add_field(name="!online",value="Returns number of online members present")
        embed.add_field(name="!role",value="Returns number of members under each role")
        await message.channel.send(content=None, embed=embed)

    elif message.content == "!online":        # To find out number of online members

        list_members = message.guild.members
        count_online_members = message.guild.member_count
        for i in list_members:
            if str(i.status)=="offline" or bool(i.bot):
                count_online_members-=1
        
        await message.channel.send(f"# of Online Members: {count_online_members}")       

    elif message.content == "!role":         # To find out number of members under each role

        list_members = message.guild.members
        roles_count = {}
        for i in list_members:
            member_roles = i.roles
            for j in member_roles:
                if j in roles_count:
                    roles_count[j]+=1
                else:
                    roles_count[j]=1
        await message.channel.send(f"Roles :- Members")
        for i in roles_count.keys():
            if str(i.name)[0]=="@":
                await message.channel.send(f"{str(i.name)[1:]} :- {roles_count[i]}")
            else:
                await message.channel.send(f"{str(i.name)} :- {roles_count[i]}")

    print("GitHub" in str(message.author.name))
    print(message.author.bot)
    if ("GitHub" in str(message.author.name) and message.author.bot):      #To send emails when a Github Pull request is made
        print("in")
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

            cur.execute("SELECT email from DISCORDBOT where channel='%s' and server='%s'" % (str(message.channel.name)+str(message.channel.id),str(message.guild)+str(message.guild.id)))
            rows = cur.fetchall()
            print(i)
            for i in rows:
                if(i[0]!="Not Updated"):
                    smtp.sendmail(EMAIL_ADDRESS,i[0],msg)
                    print("Email sent")
    conn.commit()
    cur.close()
    conn.close()


# To remove the member from the database
@client.event
async def on_member_remove(member):
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    print("Member removed part")
    print(str(member.name),str(member.guild))
    cur.execute("DELETE from DISCORDBOT where USERNAME='%s' and server='%s' and userid = '%s';" % (str(member.name),str(member.guild)+str(member.guild.id),str(member.id)))
    conn.commit()
    cur.close()
    conn.close()


# To remove this channel from the database
@client.event
async def on_private_channel_delete(channel):
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    cur.execute("DELETE from DISCORDBOT where channel='%s' and server='%s';" % (str(channel.name)+str(channel.id),str(channel.guild)+str(channel.guild.id)))
    conn.commit()
    cur.execute("DELETE from MESSAGES where channel='%s' and server='%s';" % (str(channel.name)+str(channel.id),str(channel.guild)+str(channel.guild.id)))
    conn.commit()
    cur.close()
    conn.close()


# To remove this channel from the database
@client.event
async def on_guild_channel_delete(channel):
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    cur.execute("DELETE from DISCORDBOT where channel='%s' and server='%s';" % (str(channel.name)+str(channel.id),str(channel.guild)+str(channel.guild.id)))
    conn.commit()
    cur.execute("DELETE from MESSAGES where channel='%s' and server='%s';" % (str(channel.name)+str(channel.id),str(channel.guild)+str(channel.guild.id)))
    conn.commit()
    cur.close()
    conn.close()


# To remove the server from the database
@client.event
async def on_guild_remove(guild):
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    print("Removed from guild")
    cur.execute("DELETE from DISCORDBOT where server='%s';" % (str(guild)+str(guild.id)))
    conn.commit()
    cur.execute("DELETE from MESSAGES where server='%s';" % (str(guild)+str(guild.id)))
    conn.commit()
    cur.close()
    conn.close()


# To update the channel in the database
@client.event
async def on_guild_channel_update(before, after):
    print(str(after.name)+str(after.id), str(before.guild)+str(before.id))
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    cur.execute("UPDATE DISCORDBOT set CHANNEL = '%s' where server = '%s' " % (str(after.name)+str(after.id), str(before.guild)+str(before.guild.id)))
    print("channel is updated DISCORDBOT table")
    conn.commit()
    cur.execute("UPDATE MESSAGES set CHANNEL = '%s' where server = '%s' " % (str(after.name)+str(after.id), str(before.guild)+str(before.guild.id)))
    print("channel is updated MESSAGES table")
    conn.commit()
    cur.close()
    conn.close()


# To update the channel in the database
@client.event
async def on_private_channel_update(before, after):
    print(str(after.name)+str(after.id), str(before.guild)+str(before.id))
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    cur.execute("UPDATE DISCORDBOT set CHANNEL = '%s' where server = '%s' " % (str(after.name)+str(after.id), str(before.guild)+str(before.guild.id)))
    print("channel is updated DISCORDBOT table")
    conn.commit()
    cur.execute("UPDATE MESSAGES set CHANNEL = '%s' where server = '%s' " % (str(after.name)+str(after.id), str(before.guild)+str(before.guild.id)))
    print("channel is updated MESSAGES table")
    conn.commit()
    cur.close()
    conn.close()


# To update the member in the database
@client.event
async def on_member_update(before, after):
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    role_str=[]
    role=after.roles
    for i in role:
        role_str.append(str(i.name))
    cur.execute("UPDATE DISCORDBOT set ROLES = '%s' where server = '%s' and username = '%s' and userid = '%s'" % (str("!.#$%".join(role_str)), str(before.guild)+str(before.guild.id), str(after.name), str(after.id)))
    print("roles is updated DISCORDBOT table")
    conn.commit()
    cur.close()
    conn.close()


# To update the member in the database
@client.event
async def on_user_update(before, after):
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    print(str(after.name), str(before.name), str(before.id))
    cur = conn.cursor()
    cur.execute("UPDATE DISCORDBOT set USERNAME = '%s' where username = '%s' and userid = '%s'" % (str(after.name), str(before.name), str(before.id)))
    print("roles is updated DISCORDBOT table")
    conn.commit()
    cur.close()
    conn.close()


# To update the channel in the database
@client.event
async def on_guild_update(before, after):   
    conn = psycopg2.connect(database = config('database'), user = config('user'), password = config('password'), host = config('host'), port = config('port'))
    print ("Opened database successfully")
    cur = conn.cursor()
    cur.execute("UPDATE DISCORDBOT set CHANNEL = '%s' where server = '%s' " % (str(after.name)+str(after.id), str(before.guild)+str(before.guild.id)))
    print("channel is updated DISCORDBOT table")
    conn.commit()
    cur.execute("UPDATE MESSAGES set CHANNEL = '%s' where server = '%s' " % (str(after.name)+str(after.id), str(before.guild)+str(before.guild.id)))
    print("channel is updated MESSAGES table")
    conn.commit()
    cur.close()
    conn.close()


client.run(config('token'))