import json, os
import discord
import asyncio
import logging
import random
from emoji import emojize as emojiA

import roles
import signups

def emoji(s):
	return emojiA(s, use_aliases=True)

### Basic Configuration and setup

config = {}
with open("config.json", "r") as f:
	config = json.loads(f.read())

#with open("users.json", "r") as f:
#	users = json.loads(f.read())

loglevel = config.get("log-level", logging.INFO)
if loglevel:
	loglevel = {
		"CRITICAL": logging.CRITICAL,
		"ERROR": logging.ERROR,
		"WARNING": logging.WARNING,
		"INFO": logging.INFO,
		"DEBUG": logging.DEBUG,
		"NOTSET": logging.NOTSET
	}.get(loglevel, logging.INFO)

logging.basicConfig(filename=config.get("log-file"), level=loglevel)
log = logging.getLogger() # TODO: split features into files probably

async def change_status():
	ls = config.get("status-list", [])
	if not ls:
		return # don't bother if we don't have any
	while True:
		status = random.choice(ls)
		await client.change_presence(game=discord.Game(name=status))
		await asyncio.sleep(config.get("presence-timer", 3600))

### Discord setup and boilerplate

client = discord.Client()

@client.event
async def on_ready():
	loop = asyncio.get_event_loop()
	loop.create_task(change_status())
	print("test")

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	ls = message.content.split(" ")
	if not ls[0].startswith("!"):
		return

	func = commands.get(ls[0][1:], None)
	if not func:
		return

	try:
		await func(client, message, ls[1:])
	except Exception as e:
		log.error("Unhandled exception caught for command '{}': {}".format(ls[0], e))


@client.event
async def on_reaction_add(reaction, user):
	await signups._on_reaction_add(client, reaction, user)

# TODO: make this "plugin" system work a little better...
signups.config = config.get("signups",{})
roles.config = config.get("roles",{})

commands = {
	"post": signups._post,
	"active": roles._active,

}

loop = asyncio.get_event_loop()

async def main():
	count = 0
	while True:
		try:
			await client.login(config["token"])
			await client.connect()
			count = 0
		except Exception as e:
			log.error("Something went wrong: {}".format(str(e)))

		await asyncio.sleep(5)
		count += 1

		if count >= 30:
			log.error("Detected too many failed reconnects, giving up I suppose")
			return

loop.run_until_complete(main())

