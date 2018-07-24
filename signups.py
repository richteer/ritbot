import asyncio
import discord
from datetime import datetime
from emoji import emojize as emojiA
from ritutils import channelbind, rolebind

config = {}

def emoji(s):
	return emojiA(s, use_aliases=True)

class SignupPost():
	ATTEND = 0
	BAIL = 1
	MAYBE = 2
	LATE = 3

	def __init__(self, client, channel, text):
		self.client = client
		self.channel = channel
		self.text = text

		self.responses = {}

	async def init(self):
		self.post = await self.client.send_message(self.channel, self.generate_message())
		await asyncio.sleep(0.25)
		await self.client.add_reaction(self.post, emoji(":white_check_mark:"))
		await asyncio.sleep(0.25)
		await self.client.add_reaction(self.post, emoji(":x:"))
		await asyncio.sleep(0.25)
		await self.client.add_reaction(self.post, emoji(":question:"))
		await asyncio.sleep(0.25)
		await self.client.add_reaction(self.post, emoji(":clock10:"))

	async def update(self):
		await self.client.edit_message(self.post, self.generate_message())

	def attend(self, user):
		self.responses[str(user)] = (user, self.ATTEND, datetime.now())
	def bail(self, user):
		self.responses[str(user)] = (user, self.BAIL, datetime.now())
	def maybe(self, user):
		self.responses[str(user)] = (user, self.MAYBE, datetime.now())
	def late(self, user):
		self.responses[str(user)] = (user, self.LATE, datetime.now())

	def generate_message(self):
		tmp = sorted(self.responses.values(), key=lambda x: x[2])
		# Sort by the local timestamp of when this person reacted (always take last one)
		attend = [u[0].display_name for u in tmp if u[1] == SignupPost.ATTEND]
		bail   = [u[0].display_name for u in tmp if u[1] == SignupPost.BAIL]
		maybe  = [u[0].display_name for u in tmp if u[1] == SignupPost.MAYBE]
		late   = [u[0].display_name for u in tmp if u[1] == SignupPost.LATE]

		role = discord.utils.get(self.channel.server.roles, name=config["ping-role"])

		ret = '''
{0}

{1} Please react with one of the following:
:white_check_mark: - I can make it
:x: - I cannot make it
:question: - Maybe
:clock10: - Going to be late
'''.format(self.text, role.mention)

		if attend:
			ret += "\n**Attending** ({0}):\n{1}\n".format(len(attend), "\n".join(attend))
		if maybe:
			ret += "\n**Maybe** ({0}):\n{1}\n".format(len(maybe), "\n".join(maybe))
		if late:
			ret += "\n**Late** ({0}):\n{1}\n".format(len(late), "\n".join(late))
		if bail:
			ret += "\n**Unavailable** ({0}):\n{1}\n".format(len(bail), "\n".join(bail))

		return ret


post_cache = {}

@channelbind(["signups"])
@rolebind(["Officer"])  # should be handled by discord perms, but to be safe
async def _post(client, msg, arg):
	channel = msg.channel
	await client.delete_message(msg)
	await asyncio.sleep(1.0)
	pst = SignupPost(client, channel, " ".join(arg))
	await pst.init()
	post_cache[pst.post.id] = pst


@channelbind(["signups"])
async def _on_reaction_add(client, reaction, user):
	# Ignore reactions on non-signup posts
	if user == client.user:
		return

	pst = post_cache.get(reaction.message.id)
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
