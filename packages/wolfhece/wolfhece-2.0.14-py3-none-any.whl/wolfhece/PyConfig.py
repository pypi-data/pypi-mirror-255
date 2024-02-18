import os
import json
from enum import Enum
from pathlib import Path
import logging

import wx
from .PyTranslate import _

class ConfigurationKeys(Enum):
    """ Using enumerated keys make sure we
    can check value names at code write time
    (i.e. we don't use string which are brittle)
    """
    VERSION = "Version"
    PLAY_WELCOME_SOUND = "PlayWelcomeSound"
    TICKS_SIZE = "TicksSize"
    TICKS_BOUNDS = "TicksBounds"
    COLOR_BACKGROUND = "ColorBackground"

class WolfConfiguration:
    """ Holds the PyWolf configuration.
    """

    def __init__(self, path=None):
        # We make sure we use a standard location
        # to store the configuration
        if path is None:
            if os.name == "nt":
                # On Windows NT, LOCALAPPDATA is expected to be defined.
                # (might not be true in the future, who knows)
                self._options_file_path = Path(os.getenv("LOCALAPPDATA")) / "wolf.conf"
            else:
                self._options_file_path = Path("wolf.conf")
        else:
            self._options_file_path = path

        #Set default -- useful if new options are inserted
        # --> ensuring that default values are created even if not stored in the options file
        self.set_default_config()
        if self._options_file_path.exists():
            self.load()
        else:
            # self.set_default_config()
            # This save is not 100% necessary but it helps
            # to make sure a config file exists.
            self.save()

    @property
    def path(self) -> Path:
        """ Where the configuration is read/saved."""
        return self._options_file_path

    def set_default_config(self):
        self._config = {
            ConfigurationKeys.VERSION.value: 1,
            ConfigurationKeys.PLAY_WELCOME_SOUND.value: True,
            ConfigurationKeys.TICKS_SIZE.value: 500.,
            ConfigurationKeys.TICKS_BOUNDS.value: True,
            ConfigurationKeys.COLOR_BACKGROUND.value: [255, 255, 255, 255]
        }
        self._types = {
            ConfigurationKeys.VERSION.value: int,
            ConfigurationKeys.PLAY_WELCOME_SOUND.value: bool,
            ConfigurationKeys.TICKS_SIZE.value: float,
            ConfigurationKeys.TICKS_BOUNDS.value: bool,
            ConfigurationKeys.COLOR_BACKGROUND.value: list
        }


        self._check_config()

    def _check_config(self):
        assert self._config.keys() == self._types.keys()
        for idx, (key,val) in enumerate(self._config.items()):
            assert type(val) == self._types[key]

    def load(self):
        with open(self._options_file_path, "r", encoding="utf-8") as configfile:
            filecfg = json.loads(configfile.read())

        for curkey in filecfg.keys():
            if curkey in self._config.keys():
                self._config[curkey] = filecfg[curkey]

        self._check_config()

    def save(self):
        # Make sure to write the config file only if it can
        # be dumped by JSON.
        txt = json.dumps(self._config, indent=1)
        with open(self._options_file_path, "w", encoding="utf-8") as configfile:
            configfile.write(txt)

    def __getitem__(self, key: ConfigurationKeys):
        assert isinstance(key, ConfigurationKeys), "Please only use enum's for configuration keys."
        return self._config[key.value]

    def __setitem__(self, key: ConfigurationKeys, value):
        # A half-measure to ensure the config structure
        # can be somehow validated before run time.
        assert isinstance(key, ConfigurationKeys), "Please only use enum's for configuration keys."

        self._config[key.value] = value
        self._check_config()


class GlobalOptionsDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(GlobalOptionsDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((400, 200))
        self.SetTitle(_("Global options"))

    def push_configuration(self, configuration):
        self.cfg_welcome_voice.SetValue(configuration[ConfigurationKeys.PLAY_WELCOME_SOUND])
        self.cfg_ticks_size.SetValue(str(configuration[ConfigurationKeys.TICKS_SIZE]))
        self.cfg_ticks_bounds.SetValue(configuration[ConfigurationKeys.TICKS_BOUNDS])
        self.cfg_bkg_color.SetColour(configuration[ConfigurationKeys.COLOR_BACKGROUND])

    def pull_configuration(self, configuration):
        configuration[ConfigurationKeys.PLAY_WELCOME_SOUND] = self.cfg_welcome_voice.IsChecked()
        configuration[ConfigurationKeys.TICKS_SIZE] = float(self.cfg_ticks_size.Value)
        configuration[ConfigurationKeys.TICKS_BOUNDS] = self.cfg_ticks_bounds.IsChecked()
        configuration[ConfigurationKeys.COLOR_BACKGROUND] = list(self.cfg_bkg_color.GetColour())

    def InitUI(self):

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Panel 'Miscellaneous'
        pnl = wx.ScrolledWindow(self)

        sb = wx.StaticBox(pnl, label=_('Miscellaneous'))
        sbs = wx.StaticBoxSizer(sb , orient=wx.VERTICAL)

        self.cfg_welcome_voice = wx.CheckBox(pnl, label=_('Welcome voice'))
        sbs.Add(self.cfg_welcome_voice)

        self.cfg_bkg_color = wx.ColourPickerCtrl(pnl, colour=(255,255,255,255))
        sbs.Add(self.cfg_bkg_color)

        pnl.SetSizer(sbs)
        pnl.Layout()
        vbox.Add(pnl, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)

        ### Panel 'Copy to clipboard'
        pnl = wx.ScrolledWindow(self)

        sb = wx.StaticBox(pnl, label=_('Copy to clipboard'))
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        hboxticks = wx.BoxSizer(wx.HORIZONTAL)
        self.label_ticks_size = wx.StaticText(pnl, label=_('Default ticks size for copy to clipboard'))
        self.cfg_ticks_size = wx.TextCtrl(pnl, value='500.',style = wx.TE_CENTRE )
        hboxticks.Add(self.label_ticks_size, 1, wx.EXPAND)
        hboxticks.AddSpacer(5)
        hboxticks.Add(self.cfg_ticks_size, 0, wx.EXPAND)

        sbs.Add(hboxticks, 1, wx.EXPAND)

        self.cfg_ticks_bounds = wx.CheckBox(pnl, label=_('Add bounds to ticks'))
        sbs.Add(self.cfg_ticks_bounds, 1, wx.EXPAND, 5)

        pnl.SetSizer(sbs)
        pnl.Layout()
        vbox.Add(pnl, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)

        # Buttons
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, label=_('Ok'))
        okButton.SetDefault()
        closeButton = wx.Button(self, label=_('Close'))
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        self.Layout()

        okButton.Bind(wx.EVT_BUTTON, self.OnOk)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnOk(self, e):
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    def OnClose(self, e):
        self.Destroy()

def handle_configuration_dialog(wxparent, configuration):
    dlg = GlobalOptionsDialog(wxparent)
    try:
        dlg.push_configuration(configuration)

        if dlg.ShowModal() == wx.ID_OK:
            # do something here
            dlg.pull_configuration(configuration)
            configuration.save()
            logging.info(_('Configuration saved in {}').format(str(configuration.path)))
        else:
            # handle dialog being cancelled or ended by some other button
            pass
    finally:
        # explicitly cause the dialog to destroy itself
        dlg.Destroy()


if __name__ == "__main__":
    cfg = WolfConfiguration(Path("test.conf"))
    cfg[ConfigurationKeys.PLAY_WELCOME_SOUND] = False
    print(cfg._config)
    cfg.save()
    cfg = WolfConfiguration(Path("test.conf"))
    cfg.load()
    print(cfg[ConfigurationKeys.PLAY_WELCOME_SOUND])
