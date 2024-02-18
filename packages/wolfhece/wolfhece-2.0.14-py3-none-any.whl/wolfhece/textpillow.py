from os.path import exists, join, realpath, dirname
from queue import PriorityQueue
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import logging
from enum import Enum

class Font_Priority(Enum):
    WIDTH=0
    HEIGHT=1
    FONTSIZE=2

def load_font(fontname:str, fontsize:int=10):
    if exists(fontname):
        font=ImageFont.truetype(fontname,fontsize)
    elif exists(join(join(dirname(realpath(__file__)),'fonts'),fontname)):
        font=ImageFont.truetype(join(join(dirname(realpath(__file__)),'fonts'),fontname),fontsize)
    else:
        logging.error("Font file not found -- Check your parameter")

    return font

class Text_Infos():
    """ Properties of Text_Image Class """
    def __init__(self,
                 priority=Font_Priority.WIDTH,
                 orientationbase=(1,0),
                 fontname="arial.ttf",
                 fontsize=10,
                 colour=(0,0,0,255),
                 dimspix=(100,100),
                 dimsreal=(0,0)) -> None:

        self.lengthpix = dimspix[0] # length in pixels
        self.heightpix = dimspix[1] # height in pixels

        self.lengthreal = dimsreal[0] # length in real coordinates
        self.heightreal = dimsreal[1] # height in real coordinates

        self.scalex = 1 # scale factor along X
        self.scaley = 1 # scale factor along Y

        self.orientationbase = orientationbase # orientation unit vector - example : (1,0) -> along X, (0,1) -> along Y, (1/sqrt(2),1/sqrt(2)) -> 45°

        self.priority = priority # WIDTH respect width, HEIGHT respect height, FONTSIZE respect font size :-)

        self.fontname = fontname # .ttf file name
        self.fontsize = fontsize # Font size
        self.colour = colour     # RGBA - (R,G,B,A)

        # self.language = 'fr'

    def setsize_pixels(self,w,h):

        self.lengthpix = w
        self.heightpix = h

    def setsize_real(self,wh=(0,0),scales=(0,0)):
        """Evalue la taille en pixel sur base de la taille réelle

        Args:
            w (float): largeur dans le système réel
            h (float): hauteur dans le système réel
            scales (tuple, optional): Facteur d'échelle selon x et y. Defaults to (0,0)

            Le facteur d'échelle est évalué comme le rapport entre la taille en pixel et la taille réelle.
            Exemple : 0.5 --> 2x plus petit en pixels qu'en réel.
        """
        if self.priority == Font_Priority.FONTSIZE:
            return

        if scales != (0,0):
            self.scalex=scales[0]
            self.scaley=scales[1]

        if wh!=(0,0):
            self.lengthreal=wh[0]
            self.heightreal=wh[1]

        self.lengthpix = self.lengthreal*self.scalex
        self.heightpix = self.heightreal*self.scaley

    def findsize(self,text:str):
        """Trouve la taille en pixel sur base du texte et de la taille de police en cours

        Args:
            text (str): Texte à utiliser
        """

        font = load_font(self.fontname, self.fontsize)

        left,top,right,bottom = font.getbbox(text) #, language=self.language)

        self.lengthpix = right-left
        self.heightpix = bottom-top

    def adapt_fontsize(self,text):

        old = self.fontsize

        if self.priority == Font_Priority.FONTSIZE:
            return not old==self.fontsize

        w = self.lengthpix
        h = self.heightpix

        self.findsize(text)

        scalex=1
        scaley=1
        if w!=0:
            scalex = self.lengthpix / w
        if h!=0:
            scaley = self.heightpix / h

        if self.priority == Font_Priority.WIDTH:
            self.fontsize = int(self.fontsize/scalex)
        elif self.priority == Font_Priority.HEIGHT:
            self.fontsize = int(self.fontsize/scaley)

        self.fontsize=min(self.fontsize,200)

        self.findsize(text)

        return abs(old-self.fontsize)>3

    def findscale(self,dx,dy,w,h):

        self.scalex = w/dx
        self.scaley = h/dy

    def setscale(self,sx=1,sy=1):

        self.scalex = sx
        self.scaley = sy

        if self.scalex == 0:
            self.scalex=1.
        if self.scaley == 0:
            self.scaley=1.

    def getcorners(self, xcenter, ycenter):

        orientx = self.orientationbase
        orienty = (-orientx[1], orientx[0])

        if self.scalex == 0:
            self.scalex=1.
        if self.scaley == 0:
            self.scaley=1.

        l2scale = self.lengthpix/self.scalex/2
        h2scale = self.heightpix/self.scaley/2

        x1 = xcenter - orienty[0]*h2scale - orientx[0]*l2scale
        x2 = xcenter - orienty[0]*h2scale + orientx[0]*l2scale
        x3 = xcenter + orienty[0]*h2scale + orientx[0]*l2scale
        x4 = xcenter + orienty[0]*h2scale - orientx[0]*l2scale

        y1 = ycenter - orienty[1]*h2scale - orientx[1]*l2scale
        y2 = ycenter - orienty[1]*h2scale + orientx[1]*l2scale
        y3 = ycenter + orienty[1]*h2scale + orientx[1]*l2scale
        y4 = ycenter + orienty[1]*h2scale - orientx[1]*l2scale

        x=[x1,x2,x3,x4]
        y=[y1,y2,y3,y4]

        return x,y

    def getminmax(self, xcenter, ycenter):

        x,y = self.getcorners(xcenter,ycenter)
        return np.min(x),np.max(x),np.min(y),np.max(y)

class Text_Image():

    def __init__(self,
                 text:str,
                 proptext:Text_Infos) -> None:

        self.text     = text
        self.width    = proptext.lengthpix
        self.height   = proptext.heightpix
        self.fontname = proptext.fontname
        self.color    = proptext.colour
        # self.language = 'fr'

        self._font10 = load_font(self.fontname, 10)

        self.priority = proptext.priority

        self._image:Image = None

        if proptext.priority == Font_Priority.FONTSIZE:
            self.cur_sizefont = proptext.fontsize
        else:
            self.cur_sizefont = 10

        self.create_image()

    @property
    def image(self) -> Image:
        return self._image

    def create_image(self):

        if self.priority == Font_Priority.WIDTH:
            left,top,right,bottom = self._font10.getbbox(self.text) #, language=self.language)
            scale = self.width/(right-left)
            self.cur_sizefont = int(10*scale)

        elif self.priority == Font_Priority.HEIGHT:
            left,top,right,bottom = self._font10.getbbox(self.text) #, language=self.language)
            scale = self.height/(bottom-top)
            self.cur_sizefont = int(10*scale)

        elif self.priority == Font_Priority.FONTSIZE:
            scale = 1

        self.curfont = load_font(self.fontname, self.cur_sizefont)

        self.imagemask = self.curfont.getmask(self.text) #, language=self.language) #, mode="L")
        left,top,right,bottom = self.curfont.getbbox(self.text) #, language=self.language)

        self._image = Image.new('RGBA',self.imagemask.size,(255,255,255,0))
        drawer = ImageDraw.Draw(self._image)
        drawer.text((0,-top),
                    text=self.text,
                    font=self.curfont,
                    fill=self.color)

    def show_image(self):
        self._image.show()

if __name__=='__main__':

    myprop = Text_Infos(Font_Priority.WIDTH,fontname="sanserif.ttf",colour=(50,255,60,255))
    myprop.lengthpix=300

    myprop.adapt_fontsize('test')

    myprop = Text_Infos(Font_Priority.WIDTH,fontname="arial.ttf",colour=(50,255,60,255))
    myprop.lengthpix=300
    mytest = Text_Image("Test",myprop)
    mytest.show_image()

    myprop = Text_Infos(Font_Priority.HEIGHT,fontname="arial.ttf",colour=(50,255,60,255))
    myprop.heightpix=300
    mytest = Text_Image("Test", myprop)
    mytest.show_image()

    myprop = Text_Infos(Font_Priority.WIDTH,fontname="arial.ttf",colour=(50,255,60,255))
    myprop.setsize_real((300,200),(1,1))
    mytest = Text_Image("Test",myprop)
    mytest.show_image()

    myprop = Text_Infos(Font_Priority.WIDTH,fontname="arial.ttf",colour=(50,255,60,255))
    myprop.setsize_real((300,200),(.5,.5))
    mytest = Text_Image("Test",myprop)
    mytest.show_image()

    myprop = Text_Infos(Font_Priority.WIDTH,fontname="arial.ttf",colour=(50,255,60,255))
    myprop.setsize_real((300,200),(.5,.5))
    mytest = Text_Image("Test éàç$ùö",myprop)
    mytest.show_image()

    myprop = Text_Infos(Font_Priority.HEIGHT,fontname="arial.ttf",colour=(50,255,60,255))
    myprop.setsize_real((300,500),(.5,.5))
    mytest = Text_Image("Test éàç$ùö",myprop)
    mytest.show_image()
