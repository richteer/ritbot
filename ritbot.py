import json, os
import discord
import asyncio
import logging
from emoji import emojize as emojiA


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


### Discord setup and boilerplate

client = discord.Client()

@client.event
async def on_ready():
	pass

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
	# Ignore reactions on non-signup posts
	if user == client.user:
		return

	pst = signups.post_cache.get(reaction.message.id)
	if not pst:
		return

	if reaction.emoji == emoji(":white_check_mark:"):
		pst.attend(user)
	elif reaction.emoji == emoji(":x:"):
		pst.bail(user)
	elif reaction.emoji == emoji(":question:"):
		pst.maybe(user)
	elif reaction.emoji == emoji(":clock10:"):
		pst.late(user)

	try:
		await client.remove_reaction(reaction.message, reaction.emoji, user)
	except Exception as e:
		print(e)

	await asyncio.sleep(0.3)

	await pst.update()


commands = {
	"post": signups._post,
#	"roles": _roles,

}


client.run(config["token"])
