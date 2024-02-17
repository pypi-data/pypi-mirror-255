import wx
from wolfhece.PyGui import Wolf2DModel

def main():
    ex = wx.App()
    mydro=Wolf2DModel()
    ex.MainLoop()

if __name__=='__main__':
    main()
    