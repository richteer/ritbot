import asyncio
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
		self.responses[str(user)] = (user, self.ATTEND)
	def bail(self, user):
		self.responses[str(user)] = (user, self.BAIL)
	def maybe(self, user):
		self.responses[str(user)] = (user, self.MAYBE)
	def late(self, user):
		self.responses[str(user)] = (user, self.LATE)

	def generate_message(self):
		attend = [u[0].name for u in self.responses.values() if u[1] == SignupPost.ATTEND]
		bail   = [u[0].name for u in self.responses.values() if u[1] == SignupPost.BAIL]
		maybe  = [u[0].name for u in self.responses.values() if u[1] == SignupPost.MAYBE]
		late   = [u[0].name for u in self.responses.values() if u[1] == SignupPost.LATE]

		ret = '''
{}

Please react with one of the following:
:white_check_mark: - I can make it
:x: - I cannot make it
:question: - Maybe
:clock10: - Going to be late
'''.format(self.text)

		if attend:
			ret += "\nAttending:\n{}\n".format("\n".join(attend))
		if bail:
			ret += "\nBailing\n{}\n".format("\n".join(bail))
		if maybe:
			ret += "\nMaybe\n{}\n".format("\n".join(maybe))
		if late:
			ret += "\nLate\n{}\n".format("\n".join(late))

		return ret


post_cache = {}


async def _post(client, msg, arg):
	channel = msg.channel
	await client.delete_message(msg)
	await asyncio.sleep(1.0)
	pst = SignupPost(client, channel, " ".join(arg))
	await pst.init()
	post_cache[pst.post.id] = pst
