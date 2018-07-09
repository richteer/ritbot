import asyncio
import discord
from datetime import datetime
from emoji import emojize as emojiA

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
		attend = [u[0].name for u in tmp if u[1] == SignupPost.ATTEND]
		bail   = [u[0].name for u in tmp if u[1] == SignupPost.BAIL]
		maybe  = [u[0].name for u in tmp if u[1] == SignupPost.MAYBE]
		late   = [u[0].name for u in tmp if u[1] == SignupPost.LATE]

		role = discord.utils.get(self.channel.server.roles, name="Raider")

		ret = '''
{0}

{1} Please react with one of the following:
:white_check_mark: - I can make it
:x: - I cannot make it
:question: - Maybe
:clock10: - Going to be late
'''.format(self.text, role.mention)

		if attend:
			ret += "\nAttending:\n{}\n".format("\n".join(attend))
		if maybe:
			ret += "\nMaybe:\n{}\n".format("\n".join(maybe))
		if late:
			ret += "\nLate:\n{}\n".format("\n".join(late))
		if bail:
			ret += "\nUnavailable:\n{}\n".format("\n".join(bail))

		return ret


post_cache = {}


async def _post(client, msg, arg):
	channel = msg.channel
	await client.delete_message(msg)
	await asyncio.sleep(1.0)
	pst = SignupPost(client, channel, " ".join(arg))
	await pst.init()
	post_cache[pst.post.id] = pst