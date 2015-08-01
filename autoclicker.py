import wx
from win32api import GetCursorPos, SetCursorPos, mouse_event
#for the VK keycodes
from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, MOD_ALT, VK_F1
import threading
import time

EVT_RESULT_ID = wx.NewId()
HOTKEY_ID = wx.NewId()


class ResultEvent(wx.PyEvent):
    '''Simple event to carry arbitrary result data'''
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class WorkerThread(threading.Thread):
    '''Worker Thread Class.'''
    def __init__(self, notify_window, timer, debug):
        threading.Thread.__init__(self)
        self.debug = debug
        self._notify_window = notify_window
        self._want_abort = False
        self.timer = timer
        self.start()

    def run(self):
        while True:
            time.sleep(self.timer)
            self.mouseClick()
            if self._want_abort:
                wx.PostEvent(self._notify_window, ResultEvent(None))
                break
            if self.debug:
                print self.timer

    def mouseClick(self):
        x,y = GetCursorPos()
        SetCursorPos((x, y))
        mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(self.timer)
        mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        
    def abort(self):
        self._want_abort = True


class MainFrame(wx.Frame):
    '''Main application window'''
    def __init__(self, parent, title):
        wx.Frame.__init__(self,
            parent,
            title=title,
            size=(400, 200),
            style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)

        self.initialize_properties()
        self.build_ui()
        self.register_hotkey()

    def initialize_properties(self):
        self.running = False
        self.debug = False
        self.worker = None
        self.frequency = 400

    def build_ui(self):
        self.SetBackgroundColour("white")

        self.freq_slider = wx.Slider(self,
            value=self.frequency,
            minValue=1,
            maxValue=3000, # any higher than this is unrealistic
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.freq_slider.SetTickFreq(200)

        self.debug_checkbox = wx.CheckBox(self, label="Debug Mode")

        self.home_link = wx.HyperlinkCtrl(self,
            label="[Homepage]",
            url="https://github.com/devoidfury/AutoClicker")

        self.statusbar = self.CreateStatusBar(2, style=0)
        self.statusbar.SetStatusText("Hotkey: Alt+F1", 0)
        self.statusbar.SetStatusText("\t\tOFF", 1)

        sizer = wx.FlexGridSizer(vgap=1, hgap=1, cols=1, rows=2)

        padding = 3
        box1 = wx.BoxSizer(wx.VERTICAL)
        box1.Add(self.freq_slider, 0, wx.EXPAND|wx.ALL, padding)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.debug_checkbox, 1, wx.EXPAND|wx.ALL, padding)
        box2.Add(self.home_link, 0, wx.ALIGN_RIGHT|wx.ALL, padding)

        sizer.Add(box1, 1, wx.EXPAND | wx.ALL)
        sizer.Add(box2, 0, wx.EXPAND)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)

        self.SetSizerAndFit(sizer)
        self.Fit()

    def register_hotkey(self):
        '''This function registers the hotkey Alt+F1'''
        self.RegisterHotKey(
            HOTKEY_ID, #a unique ID for this hotkey
            MOD_ALT, #the modifier key
            VK_F1) #the key to watch for

        self.Bind(wx.EVT_HOTKEY, self.handle_hotkey, id=HOTKEY_ID)

    def handle_hotkey(self, evt):
        self.running = not self.running
        if self.running:
            self.debug = self.debug_checkbox.GetValue()
            self.frequency = self.freq_slider.GetValue()
            self.worker = WorkerThread(
                notify_window=self, 
                timer=1.0/self.frequency,
                debug=self.debug)
        else:
            self.worker.abort()
            self.worker = None

        state = 'ON' if self.running else 'OFF'
        self.statusbar.SetStatusText('\t\t' + state, 1)
        print 'AutoClicker ' + state


class AutoClicker(wx.App):
    def OnInit(self):
        main = MainFrame(None, "AutoClicker")
        self.SetTopWindow(main)
        main.Show()
        return 1

if __name__ == '__main__':
    autoClicker = AutoClicker(0)
    autoClicker.MainLoop()
