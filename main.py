import time
import asyncio
import random
import certifi

import nextcord
from nextcord.ext import tasks, commands

import pymongo
from pymongo import MongoClient, InsertOne, UpdateOne

# MongoDB
ca = certifi.where()
mongo = MongoClient('', tlsAllowInvalidCertificates=True, ssl_cert_reqs=ca)
db = mongo.database.logbook
temp = mongo.database.current
status_db = mongo.database.status

# Initialising client
intents = nextcord.Intents.default()
intents.voice_states = True
intents.members = True
client = commands.Bot(command_prefix="$", case_insensitive=True, intents=intents)
client.remove_command("help")

# Client status changer
aircraftList = ['Piper Cub', 'Cessna 172', 'Alphajet PAF', 'Boeing 737-700', 'Embraer Phenom 100', 'de Havilland DHC6 Twin Otter', 'F-16 Fighting Falcon', 'Pitts Special S1', 'Eurocopter EC135', 'Airbus A380', 'Alisport Silent 2 Electro', 'Pilatus PC-7 Mk-I', 'Lockheed P-38 Lightning F-5B', 'Douglas DC-3', 'McDonnell Douglas MD-11', 'Sukhoi Su-35', 'Concorde', 'Zlin Z-50', 'Cessna 152', 'Antonov An-140', 'Evektor Sportstar', 'szd-48-3 Jantar', 'Hughes 269a/TH-55 Osage', 'Boeing 787-8', 'Embraer E190', 'Boeing 767-300ER', 'Boeing 757-200', 'Airbus A350-900', 'Boeing 777-300ER', 'Airbus A321neo', 'Airbus A330-300', 'Bombardier Dash 8 Q400', 'Boeing 747-8 Freighter', 'BAE146', 'CRJ 700', 'CRJ 900', 'Embraer 170', 'Embraer 190', 'Piper PA-28', 'Cessna Citation', 'Cessna 172', 'Mirage 2000', 'Cirrus SR22', 'Cirrus SR22 GTS Turbo', 'Boeing 737-800', 'CRJ-900', 'Airbus A340-600', 'A-10C Thunderbolt II', 'Lockheed SR-71A Blackbird', 'Boeing 787-9 Dreamliner', 'ATR 72-600', 'Cirrus Vision Jet/SF50 G2', 'Northrop Grumman B-2 Spirit', 'F-14B Tomcat ', 'Bombardier CRJ 200', 'Caproni Stipa', 'Boeing 737 Max 8', 'Antonov An-225 Mriya', 'Sikorsky S-97 Raider', 'Supermarine Spitfire Mk XIV', 'Bell UH-1H Iroquois', 'Airbus A400M Atlas', 'F-22 Raptor', 'Airbus A320-214', 'North American XB-70 Valkyrie', 'Dassault nEUROn ', 'Airbus A350-1000 XWB', 'Pilatus PC12', 'MQ9B Reaper', 'KLM Cityhopper E195-E2', 'Lockheed Martin P-791', 'Boeing 787-10 Dreamliner', 'HAL-Dornier 228-100', 'Boeing p8I Neptune']

async def loop_status():
	while True:
		await client.change_presence(activity=nextcord.Game(name=f"Flying the {random.choice(aircraftList)}"))
		await asyncio.sleep(60*15)


@client.event
async def on_ready():
	print("Online and ready.")

	client.loop.create_task(loop_status())

	global list_of_roles

	Guild = client.get_guild(553718744233541656)

	list_of_roles = {
		"Trainee_Pilot": Guild.get_role(844635858501500988),
		"Student_Pilot": Guild.get_role(553723642568114187),
		"Private_Pilot": Guild.get_role(553723641465143356),
		"Commercial_Pilot": Guild.get_role(553723640789729301),
		"Senior_Pilot": Guild.get_role(553723630643707905)
	}


@client.event
async def on_member_join(member):
	embed = nextcord.Embed(title=f"Welcome to GeoFS Events, {member.name}!", description=f"Please make sure you have read the rules!\nWe organize and host events every day, so make sure to check <#756937922904850442> and <#791093790432690217> to keep up on events hosted for that day.\nThere are currently {len(member.guild.members)} people in this server.\nIf you need any help or advice, please contact the staff team.\n\nCheck out and subscribe to our YouTube channel here:\nhttps://www.youtube.com/channel/UCZhJvrv8C6mb0FXENg6uh2w", colour=nextcord.Colour.from_rgb(88, 83, 255))
	embed.set_footer(text="We hope you enjoy your stay!")
	channel = member.guild.get_channel(837708315965915156)
	await channel.send(embed=embed)


@client.command()
async def help(ctx):
	embed = nextcord.Embed(description="Help avaliable [here](https://gist.github.com/s1072489/7758f319c74be64d3fdb1bc651ce164c)", colour=nextcord.Colour.from_rgb(88, 83, 255))
	await ctx.reply(embed=embed)


@client.command()
async def ping(ctx):
	"""Returns basic information about the bot"""

	embed = nextcord.Embed(
		title=f"{client.user.name} Stats",
		colour=ctx.author.colour
	)

	embed.add_field(name="Ping:", value=f"{round(client.latency * 1000)}ms")
	embed.add_field(name="Python Version:", value="3.10.0")
	embed.add_field(name="Nextcord Version:", value="2.0.0a3")
	embed.add_field(name="PyMongo Version:", value="3.12.0")
	embed.add_field(name="Creator:", value="<@825232373481865226>")
	await ctx.send(embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
	"""Temporary database for during the flight and calculating points."""

	status = status_db.find_one({"_id": 1})["S"]

	if status == True:
		if not before.channel and after.channel:
			# User joined a VC

			if temp.find_one({"_id": member.id}) == None:
				# Create a new user in the database
				temp.insert_one({
					"_id": member.id,
					"J": time.time(),
					"T": 0
				})
				channel = client.get_channel(895833183503917097)
				await channel.send(f"{member.mention} joined the flight.", allowed_mentions=nextcord.AllowedMentions(users=False))
			else:
				temp.find_one_and_update({"_id": member.id}, {"$set": {'J': time.time()}})
				channel = client.get_channel(895833183503917097)
				await channel.send(f"{member.mention} rejoined the flight.", allowed_mentions=nextcord.AllowedMentions(users=False))
		elif before.channel and not after.channel:
			# User left a VC

			if temp.find_one({"_id": member.id}) == None:
				# had not joined somehow
				pass
			else:
				temp.find_one_and_update({"_id": member.id}, {"$inc": {"T": round(
					time.time() - temp.find_one({"_id": member.id})["J"])}, "$set": {"J": 0}})
				channel = client.get_channel(895833183503917097)
				await channel.send(f"{member.mention} left the flight.", allowed_mentions=nextcord.AllowedMentions(users=False))


@client.command()
@commands.has_role("Staff Member")
async def start(ctx):
	"""Logs all members joining the flight VC and adds points after"""

	await ctx.trigger_typing()

	status_db.find_one_and_update({"_id": 1}, {"$set": {"S": True}})

	channel = client.get_channel(553733861234704405)
	members = channel.members

	for member in members:
		temp.insert_one({
			"_id": member.id,
			"J": time.time(),
			"T": 0
		})
		channel = client.get_channel(895833183503917097)
		await channel.send(f"{member.mention} joined the flight.", allowed_mentions=nextcord.AllowedMentions(users=False))

	await ctx.send("The flight has been started")
	await ctx.message.add_reaction("<:yes:895176594572853258>")


@client.command()
@commands.has_role("Staff Member")
async def end(ctx):
	"""Logs all members joining the flight VC"""

	await ctx.trigger_typing()

	yes = []
	no = []
	members = list(temp.find({}))
	for member in members:

		if member["J"] != 0:
			member["T"] = member["T"] + round(time.time() - member["J"])

		if member["T"] > 5*60:
			user = await client.fetch_user(member["_id"])
			if db.find_one({"_id": member["_id"]}) == None:
				db.insert_one({
					"_id": member["_id"],
					"P": 10,
					"A": 1
				})
			else:
				db.find_one_and_update(
					{"_id": member["_id"]}, {"$inc": {"P": 10}})
				db.find_one_and_update(
					{"_id": member["_id"]}, {"$inc": {"A": 1}})

			yes.append(f"User: {user.name} Time: {round(member['T']/60)}min\n")
		else:
			user = client.get_user(member["_id"])
			no.append(f"User: {user.name} Time: {round(member['T']/60)}min\n")

	status_db.find_one_and_update({"_id": 1}, {"$set": {"S": False}})
	temp.delete_many({})

	embed = nextcord.Embed(title="Flight Complete", description=f"```Valid:\n{''.join(yes)}Invalid:\n{''.join(no)}```")
	await ctx.send(embed=embed)

	await ctx.message.add_reaction("<:yes:895176594572853258>")


@client.command()
@commands.has_role("Staff Member")
async def add(ctx, member, attendance: int, points: int = None):
	"""Changes the amount of attendance / points of a member by the specified amount"""

	await ctx.trigger_typing()

	if points == None:
		points = attendance * 10

	if type(member) == str:
		member = client.get_user(
			int(member.replace("<@", "").replace("!", "").replace(">", "")))
	else:
		await ctx.reply(f"Invalid member `{member}`")
		return

	try:
		db.find_one_and_update({"_id": member.id}, {"$inc": {"A": attendance, "P": points}})
		user = db.find_one({"_id": member.id})
	except AttributeError:
		await ctx.reply("Invalid member")

	if user == None:
		# Create a new user in the database
		db.insert_one({"_id": member.id, "P": points, "A": attendance})
		user = db.find_one(member.id)

	embed = nextcord.Embed(title=f"{member.name} data", description=f"```Attendence: {user['A']}\nPoints: {user['P']}\n```")
	await ctx.reply(embed=embed)


@client.command()
async def info(ctx, member=None):
	"""Returns info about the specified member (defaults to you)"""

	await ctx.trigger_typing()

	if type(member) == str:
		member = client.get_user(
			int(member.replace("<@", "").replace("!", "").replace(">", "")))
	elif member == None:
		member = ctx.author
	else:
		await ctx.reply("Invalid member")
		return

	try:
		user = db.find_one({"_id": member.id})
	except AttributeError:
		await ctx.reply("Invalid member")

	if user == None:
		await ctx.reply(f"Could not find {member} in the Database!")
	else:
		embed = nextcord.Embed(title=f"{member} Info", description=f"```Points: {user['P']}\nAttendance: {user['A']}\n```")
		await ctx.reply(embed=embed)


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.MissingRole):
		await ctx.reply("You don't have the required roles!")
	else:
		await ctx.reply(f"```css\n[{time.strftime('%H:%M:%S', time.gmtime())} ERROR]: {error}```")
	raise error


@client.command()
async def role(ctx):
	await ctx.reply("Temporarily Disabled")


if __name__ == "__main__":
	client.run("")
