import cv2
import numpy
import rospy
from PIL import Image
import typing

EFFECTRESIZEFACTORS = {'meme': 1,
                        'mask': 4}

class RecognizeOBjectHandler:
    def __init__(self, img: numpy.ndarray, cascade_xml_url: str) -> None:
        self._img = img
        self._xml = cascade_xml_url

        self._eye_info = []

    def __addEffect(self, img: numpy.ndarray, effect: str) -> Image:
        self._eye_info = numpy.sort(self._eye_info, axis=0)

        main = Image.fromarray(img)
        ov = Image.open(f'/home/pogodigitalism/catkin_ws/src/t1_robot/resources/{effect}.png').convert('RGBA')
        w, h = ov.size

        ov = ov.resize((int(self._eye_info[0][2]*(w/h))*EFFECTRESIZEFACTORS[effect], 
                        int(self._eye_info[0][2])*EFFECTRESIZEFACTORS[effect]))

        x = abs(int(self._eye_info[0][0]+((self._eye_info[0][0]-self._eye_info[1][0])/2)))+20
        y = abs(int(self._eye_info[0][1]+((self._eye_info[0][1]-self._eye_info[1][1])/2)))+15

        main.paste(ov, (x,y), ov)
        return main


    async def exec(self, effect: str = None) -> typing.Union[numpy.ndarray, None]:
        self._eye_info.clear()

        img_gray = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
        img_rgb = cv2.cvtColor(self._img, cv2.COLOR_BGR2RGB)
        
        
        if effect:
            found: typing.Union[numpy.ndarray, tuple] = cv2.CascadeClassifier(self._xml).detectMultiScale(img_gray, minSize =(15, 15))
            
            if isinstance(found, tuple) or found.any():
                for (x, y, w, h) in found:
                    self._eye_info.append([x,y,w,h])

                if len(self._eye_info) > 1:
                    return numpy.array(self.__addEffect(img_rgb, effect))
        return img_rgb