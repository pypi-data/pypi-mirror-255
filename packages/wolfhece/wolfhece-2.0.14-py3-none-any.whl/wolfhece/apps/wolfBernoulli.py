
import wx
try:
    from ..PyTranslate import _
    from ..bernoulli.NetworkOpenGL import Bernoulli_Window
except:
    from wolfhece.PyTranslate import _
    from wolfhece.bernoulli.NetworkOpenGL import Bernoulli_Frame
import wx

def main():
    app = wx.App()
    ex = Bernoulli_Frame(None)
    ex.Show()
    app.MainLoop()

if __name__=='__main__':
    main()
