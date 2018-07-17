def channelbind(channels):
	def decorator(func):
		async def wrapper(client, msg, args):
			cname = ""
			# TODO: Find a better way to work around this stupid mess
			if msg.__class__.__name__ == "Message":
				cname = msg.channel.name
			elif msg.__class__.__name__ == "Reaction":
				cname = msg.message.channel.name

			if cname not in channels:
				return

			return await func(client, msg, args)
		return wrapper
	return decorator

def rolebind(roles):
	def decorator(func):
		async def wrapper(client, msg, args):
			for r in msg.author.roles:
				if r.name in roles:
					break
			else:
				return
			return await func(client, msg, args)
		return wrapper
	return decorator
