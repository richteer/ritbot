def channelbind(channels):
	def decorator(func):
		async def wrapper(client, msg, args):
			if msg.channel.name not in channels:
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
