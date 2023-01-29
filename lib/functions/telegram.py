import json

from telethon import TelegramClient

API_ID = 29491226
API_HASH = '13d9c062aa12d53872121db27813b9b9'


def get_recent_posts(message_count: int = 3, contained_string: str = "Update"):
    client = TelegramClient('my-client', API_ID, API_HASH)
    channel_username = 'minecraft_2d_multiplayer'

    async def main():
        count = 0
        res = {}
        async for message in client.iter_messages(channel_username):
            if message is not None and message.text is not None:
                if message.text.count(contained_string) > 0:
                    res.update({message.id: {
                        "text": message.text,
                        "author": message.post_author
                    }})
                    if message.media is not None:
                        await client.download_media(message.media, f"lib/temp/images/{message.id}.jpg")
                        res[message.id].update({"image": f"lib/temp/images/{message.id}.jpg"})
                    count += 1
            if count == message_count:
                break

        with open("lib/temp/recent_posts.json", "w") as f:
            json.dump(res, f)

    with client:
        client.loop.run_until_complete(main())
