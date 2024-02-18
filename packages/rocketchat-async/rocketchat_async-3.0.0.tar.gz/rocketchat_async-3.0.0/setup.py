# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rocketchat_async']

package_data = \
{'': ['*']}

install_requires = \
['websockets>=10.4,<11.0']

setup_kwargs = {
    'name': 'rocketchat-async',
    'version': '3.0.0',
    'description': 'asyncio-based Python wrapper for the Rocket.Chat Realtime API.',
    'long_description': '# rocketchat-async\n\nasyncio-based Python wrapper for the Rocket.Chat Realtime API.\n\n## When should you use this library?\n\nUse this library if you:\n\n- want to integrate with Rocket.Chat from Python\n- are using [asyncio](https://docs.python.org/3/library/asyncio.html) to drive your code\n- want to use Rocket.Chat\'s efficient websockets-based Realtime API\n\n## Installation\n\n`pip install rocketchat-async`\n\n## Example usage\n\n```python\nimport asyncio\nimport random\nfrom rocketchat_async import RocketChat\n\n\ndef handle_message(channel_id, sender_id, msg_id, thread_id, msg, qualifier,\n                   unread, repeated):\n    """Simply print the message that arrived."""\n    print(msg)\n\n\nasync def main(address, username, password):\n    while True:\n        try:\n            rc = RocketChat()\n            await rc.start(address, username, password)\n            # Alternatively, use rc.resume for token-based authentication:\n            # await rc.resume(address, username, token)\n\n            # A possible workflow consists of two steps:\n            #\n            # 1. Set up the desired callbacks...\n            for channel_id, channel_type in await rc.get_channels():\n                await rc.subscribe_to_channel_messages(channel_id,\n                                                       handle_message)\n            # 2. ...and then simply wait for the registered events.\n            await rc.run_forever()\n        except (RocketChat.ConnectionClosed,\n                RocketChat.ConnectCallFailed) as e:\n            print(f\'Connection failed: {e}. Waiting a few seconds...\')\n            await asyncio.sleep(random.uniform(4, 8))\n            print(\'Reconnecting...\')\n\n\n# Side note: Don\'t forget to use the wss:// scheme when TLS is used.\nasyncio.run(main(\'ws://localhost:3000/websocket\', \'username\', \'password\'))\n```\n\n## API Overview\n\nBrief overview of the currently implemented methods.\n\nAs of now, Rocket.Chat\'s API is only covered partially (based on my original\nneeds). I am open to both feature requests as well as pull requests.\n\n### Methods\n\n#### `RocketChat.get_channels()`\n\nGet a list of channels the logged-in user is currently member of.\n\n#### `RocketChat.send_message(text, channel_id, thread_id=None)`\n\nSend a text message to a channel.\n\n#### `RocketChat.send_reaction(orig_msg_id, emoji)`\n\nSend a reaction to a specific message.\n\n#### `RocketChat.send_typing_event(channel_id, is_typing)`\n\nSend the "typing" event to a channel.\n\n#### `RocketChat.subscribe_to_channel_messages(channel_id, callback)`\n\nSubscribe to all messages in the given channel. Returns the subscription ID.\n\nThe provided callback should accept eight arguments: `channel_id`,\n`sender_id`, `msg_id`, `thread_id`, `msg_text`, `msg_qualifier`\n and `repeated`. The qualifier can help to determine if e.g. the\nmessage is a system message about the user being removed from\nthe channel.  The `repeated` flag assists in distinguishing \nwhether the message has been received again as a result of \nthread replies, or if it is a new message post.\n\n#### `RocketChat.subscribe_to_channel_changes(callback)`\n\nSubscribe to all changes in channels. Returns the subscription ID.\n\nThe provided callback should accept two arguments: `channel_id`\nand `channel_qualifier`. The qualifier helps to determine e.g.\nif it\'s a direct message or a normal room.\n\n#### `RocketChat.unsubscribe(subscription_id)`\n\nCancel a subscription.\n',
    'author': 'Hynek Urban',
    'author_email': 'hynek.urban@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/hynek-urban/rocketchat-async',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
