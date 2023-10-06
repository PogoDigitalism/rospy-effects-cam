#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import asyncio
from discord_webhook import AsyncDiscordWebhook
from discord_webhook import DiscordEmbed, DiscordWebhook


class listener:
    def __init__(self, discord_whurl: str, ros_node_name: str ,ros_topic: str):
        rospy.init_node(ros_node_name)

        self._last_post_unix = 0

        self._whurl = discord_whurl
        self._rt = ros_topic

    @property
    def webhook_url(self) -> str:
        return self._whurl
    
    @webhook_url.setter
    def webhook_url(self, url: str):
        self._whurl = url

    async def __sendLog(self, log: dict) -> None:
        self._embed = DiscordEmbed(title=log['title'], description=log['description'], color="6dc5ff")

        self._webhook = AsyncDiscordWebhook(url=self._whurl, content='this is a test')
        self._webhook.add_embed(self._embed)
        self._webhook.add_file(log['filebytes'].encode(), 'test.jpg')

        hi = await self._webhook.execute()
        self._last_post_unix = rospy.get_time()

    async def __createLog(self, data: str) -> None:
        log = {'title': self._rt, 'description': ' hihi', 'filebytes' : data.data}
        print(data.data)

        await self.__sendLog(log)

    # def __sendLog(self, log: dict) -> None:
    #     print(log,' sending')
    #     self._embed = DiscordEmbed(title=log['title'], description=log['description'], color="6dc5ff")

    #     self._webhook = DiscordWebhook(url=self._whurl, content='this is a test')
    #     self._webhook.add_embed(self._embed)

    #     hi = self._webhook.execute()
    #     print('hi executed, did message arrive?')
    #     self._last_post_unix = rospy.get_time()

    # def __createLog(self, data) -> None:
    #     rospy.loginfo('creating log')

    #     log = {'title': self._rt, 'description': data.data}

    #     self.__sendLog(log)


    def __callback(self, data: str) -> None:
        if rospy.get_time() - self._last_post_unix > 5:
            self._last_post_unix = rospy.get_time()

            self._new_task = asyncio.run(self.__createLog(data))

    def setS(self) -> None:
        rospy.Subscriber(self._rt, String, self.__callback)

    async def async_spin(self) -> None:
        rospy.loginfo("beginning node spin")

        while not rospy.is_shutdown():
            pass


async def main():
    h = listener(discord_whurl='https://discord.com/api/webhooks/1158359060140265503/deUeh_5dXFbmeoNeKwnRtWAMMnM7mI_4LtyXRtkpabYSq3oHGtzjY6rbJn9oT45QNXZV', ros_node_name='R_toDiscord_node' ,ros_topic='topic_TransferImageData')
    h.setS()

    await h.async_spin()

if __name__ == '__main__':
    asyncio.run(main())