#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
import asyncio
import cv_bridge
import cv2
from cascade_gen import RecognizeOBjectHandler
import os

class listener:
    def __init__(self, ros_node_name: str ,listen_to_ros_topic: str):
        rospy.init_node(ros_node_name)

        self._last_post_unix = 0
        self._last_processing_time = 0

        self._rt = listen_to_ros_topic
        self._bridge = cv_bridge.CvBridge()


    async def __publishImage(self, bin: bytes, cv_img, pt) -> None:
        ROH = RecognizeOBjectHandler(img=cv_img, cascade_xml_url='/home/pogodigitalism/catkin_ws/src/t1_robot/resources/haarcascade_eye_tree_eyeglasses.xml')
        
        cv_img = await ROH.exec(effect='meme')
        if cv_img is not None:
            ros_img = self._bridge.cv2_to_imgmsg(cv_img, encoding='rgb8')
            try:
                self._img_pub.publish(ros_img)
            except Exception as e:
                rospy.logerr(e)

            self._pub.publish(str(bin))

            t = rospy.get_time()
            self._last_post_unix = t
            self._last_processing_time = t-pt
        

    async def __processImage(self, data: Image, pt) -> None:
        cv_img = self._bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')
        # asyncio.get_event_loop().create_task(self.__test(cv_img))

        conv_img = cv2.imencode('.jpg', cv_img)[1].tostring()
        await self.__publishImage(conv_img, cv_img, pt)


    def __callback(self, data: Image) -> None:
        if rospy.get_time() - self._last_post_unix >= self._last_processing_time:
            processing_start = rospy.get_time()

            self._last_post_unix = rospy.get_time()

            self._new_task = asyncio.run(self.__processImage(data, processing_start))


    def setS(self) -> None:
        rospy.Subscriber(self._rt, Image, self.__callback)

    def setP(self, discord_publisher: str, raw_publisher: str) -> None:
        self._pub = rospy.Publisher(discord_publisher,String, queue_size=10)

        self._img_pub = rospy.Publisher(raw_publisher, Image, queue_size=10)


    async def async_spin(self) -> None:
        rospy.loginfo("beginning node spin")

        while not rospy.is_shutdown():
            pass


async def main():
    h = listener(ros_node_name='camera_convert' ,listen_to_ros_topic='usb_cam/image_raw')
    h.setS()
    h.setP(discord_publisher='topic_TransferImageData', raw_publisher='topic_DisplayROH')

    await h.async_spin()

if __name__ == '__main__':
    asyncio.run(main())