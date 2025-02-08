from overlays import *;
from constants_en import *;
import wx;

# Main thread globals
target_window_handle = None;

# Map of window display name -> HANDLE
available_windows = {
    "test window": 0
};

# Array of IDs (TODO)
available_injection_method_ids = [];

available_overlays = {
    ID_OVERLAY_HISTORY_DEFAULT: Overlay( ID_OVERLAY_HISTORY_DEFAULT ),
    ID_OVERLAY_MOUSE_DEFAULT: Overlay( ID_OVERLAY_MOUSE_DEFAULT )
};

class MainWindow( wx.Frame ):
    # Fields:
    # - available_windows: {display_name: HANDLE}

    def __init__( self, parent, title ):
        super().__init__( parent, title=title );

        # Field inits
        self.available_windows = {};

        # Ribbon
        self.ribbon = wx.Menu();

        # Status bar
        self.CreateStatusBar();

        # Global settings panel
        self.root_panel = wx.Panel( self );
        self.root_sizer = wx.BoxSizer( wx.VERTICAL );

        # Target window selector
        self.target_window_select_sizer = wx.BoxSizer( wx.HORIZONTAL );
        self.target_window_select_label = wx.StaticText( self.root_panel, label=TEXT_TARGET_WINDOW_SELECT_LABEL );
        self.target_window_select = wx.ComboBox( self.root_panel, choices=self.get_available_target_windows(), style=wx.CB_DROPDOWN );
        self.target_window_refresh_button = wx.Button( self.root_panel, label=TEXT_TARGET_WINDOW_REFRESH_BUTTON );
        self.target_window_select.Bind( wx.EVT_COMBOBOX, self.on_select_target_window );
        self.target_window_select_sizer.Add( self.target_window_select_label, 0, wx.ALL, 5 );
        self.target_window_select_sizer.Add( self.target_window_select, 0, wx.ALL | wx.EXPAND | wx.CENTER, 5 );
        self.target_window_select_sizer.Add( self.target_window_refresh_button, 0, wx.ALL | wx.CENTER, 5 );
        
        # Hook method selector
        self.hook_method_select_sizer = wx.BoxSizer( wx.HORIZONTAL );
        self.hook_method_select_label = wx.StaticText( self.root_panel, label=TEXT_HOOK_METHOD_SELECT_LABEL );
        self.hook_method_select = wx.ComboBox( self.root_panel, choices=self.get_available_hook_methods(), style=wx.CB_DROPDOWN );
        self.hook_method_select.Bind( wx.EVT_COMBOBOX, self.on_select_hook_method );
        self.hook_method_select_sizer.Add( self.hook_method_select_label, 0, wx.ALL, 5 );
        self.hook_method_select_sizer.Add( self.hook_method_select, 0, wx.ALL | wx.EXPAND | wx.CENTER, 5 );
        
        # TODO: add overlay setting panel, make the specific frames overlap
        # Overlay menu
        self.overlay_settings_sizer = wx.BoxSizer( wx.HORIZONTAL );
        self.overlay_select = wx.ComboBox( self.root_panel, choices=available_overlay.keys(), style=wx.CB_SIMPLE );
        self.overlay_settings_panel = wx.Panel( self.overlay_panel ); # Subpanel for specific settings
        self.overlay_select.Bind( wx.EVT_COMBOBOX, self.on_select_overlay );
        self.overlay_settings_sizer.Add( self.overlay_select, 0, wx.ALL, 5 );
        self.overlay_settings_sizer.Add( self.overlay_settings_panel, wx.ALL | wx.EXPAND | wx.CENTER, 5 );

        # Overlay setting menus
        for overlay in available_overlays.values():
            self.overlay_settings_panel

        self.root_sizer.Add( self.target_window_select_sizer, 0, wx.CENTER );
        self.root_sizer.Add( self.hook_method_select_sizer, 0, wx.CENTER );
        self.root_sizer.Add( self.overlay_settings_sizer, 0, wx.CENTER );


        self.Show( True );


    # Event handlers

    def on_select_target_window( self, event ):
        """Notify overlay threads of a change in window"""
        # TODO: changes may only take effect on next 
        # Find window handle, size; notify subthreads by changing instance fields
        window_handle = self.available_windows[event.GetSelection()];

    def on_select_hook_method( self, event ):
        """Notify overlay threads of a change in hook method"""
        pass;

    def on_select_overlay( self, event ):
        """Display the selected overlay's menu"""
        overlay = available_overlays[event.GetSelection()];
        #self.overlay_panel

    # Getters

    def get_available_target_windows( self ):
        """Returns names of target windows"""
        # pywin32
        # populate field and return labels
        available_windows = {"test window": 0};
        return available_windows.keys();

    def get_available_hook_methods( self ):
        # TODO
        return available_injection_method_ids;

if __name__ == "__main__":
    app = wx.App( False );
    frame = MainWindow( None, TITLE );
    app.MainLoop();