### Key history overlay reference implementation
### @author diblenderbenzene aka AV306
### 2025

# Imports
import multiprocessing as mp;
import keyboard as kb;
from collections import deque;
from win32gui import GetForegroundWindow, FindWindow, GetWindowRect;
from ctypes import CDLL, pointer;
from ctypes.wintypes import RECT;
import pyray as rl;

from logger import *;
from animation import *;

#from typing import *;

# Default constants
OVERLAY_WINDOW_TITLE_DEFAULT: str = "history";
OVERLAY_WINDOW_HEIGHT_DEFAULT: int = 100;
OVERLAY_WINDOW_ALPHA_DEFAULT: int = 100;

MARGIN_DEFAULT: int = 10;
HISTORY_MIN_ALPHA_DEFAULT: int = 50;
FPS_DEFAULT: int = 120;
VSYNC_DEFAULT: bool = True;
KEY_HISTORY_LENGTH_DEFAULT: int = 20;

DWMAPI = CDLL( "dwmapi" );

# List of options:
# - height
# - alpha
# - fps
# - vsync
# - title
# - history length

def get_window_pos( handle ) -> tuple[int, int, int, int]:
    """Get the left, right, top, and bottom coordinated of the window with the given handle"""
    rect = RECT();
    hr = DWMAPI.DwmGetWindowAttribute( handle, 9, pointer( rect ), 16 );

    # from _dwmapi import ffi, lib;
    # # hwnd = ffi.new( "HWND" )
    # rect = ffi.new( "RECT *" );
    # lib.DwmGetWindowAttribute( handle, 9, rect, 16 );
    
    if hr != 0:
        raise RuntimeError( f"Failed to get window position: {hr}" );
    
    return rect.left, rect.top, rect.right, rect.bottom;


def create_overlay_window( width: int, height: int, fps: int, vsync: bool, title: str ) -> None:
    rl.set_config_flags(
        rl.FLAG_WINDOW_UNDECORATED
        | rl.FLAG_WINDOW_TOPMOST
        | rl.FLAG_WINDOW_TRANSPARENT
        | rl.FLAG_WINDOW_MOUSE_PASSTHROUGH
    );
    
    if fps > 0:
        rl.set_target_fps( fps );
    if vsync:
        rl.set_window_state( rl.FLAG_VSYNC_HINT );
        
    rl.init_window( width, height, title );


def cleanup() -> None:
    kb.unhook_all();
    log_info( "Cleaned up" );


def run( handle, options ):
    log_info( f"Starting overlay process for handle {handle}" );

    # Attach keyboard hook and queue
    key_history_lock = mp.Lock();
    pressed_keys: Dict[List[str, int]] = {}; # We need an ordered set here (to prevent key repeats from clogging it up, but a Dict is the closest Python has...)
    
    # Deque of arrays [key, index]
    #log_info( options.get( "history_length", KEY_HISTORY_LENGTH_DEFAULT ) )
    key_up_recent: List[List[str, int]] = []; # Stores the most recently released keys that haven't finished animation
    start_animation_flag: List[bool] = [False]; # Signal to the render thread that it should start animating the contents of `key_up_animating`; will only be unset by the render thread
    # Note: the render thread is responsible for moving the contents of `key_up_animating` into `key_up_history`
    key_up_history = deque( maxlen=options.get( "history_length", KEY_HISTORY_LENGTH_DEFAULT ) ); # Stores the rest of the keys
    # TODO: the deque needs to be periodically serialised to a file or something

    def on_key_event( event: kb.KeyboardEvent ):
        # Check window focus
        # FIXME: may have to make handle a global variable
        #if GetForegroundWindow() != handle:
        #    return;

        key_history_lock.acquire(); # Lock the deque
        key = event.name.lower();

        if event.event_type == kb.KEY_DOWN:
            # Add the key to the pressed_keys ordered set
            pressed_keys[key] = None;
        else:
            # key_up_recent.append( [key, 1] );
            # start_animation_flag[0] = True;

            if key_up_recent and key_up_recent[-1][0] == key:
                # If most recent key is this one, increment its count
                key_up_recent[-1][1] += 1;
            else:
                # Add it to the animation list and signal the render thread
                key_up_recent.append( [key, 1] );
                start_animation_flag[0] = True;

            # Remove key from key_down list
            try:
                del pressed_keys[key];
            except (ValueError, KeyError):
                pass;

        key_history_lock.release();
    
    # Attach hook
    kb.hook( on_key_event );
    
    # Rendering setup

    overlay_window_width: int = 0; # Set later
    overlay_window_height: int = options.get( "height", OVERLAY_WINDOW_HEIGHT_DEFAULT );

    overlay_alpha: int = options.get( "alpha", OVERLAY_WINDOW_ALPHA_DEFAULT );
    overlay_clear_color = rl.Color( 0, 0, 0, overlay_alpha );
    #HISTORY_MIN_ALPHA = options.get( "history_min_alpha", HISTORY_MIN_ALPHA );
    
    create_overlay_window(
        overlay_window_width, overlay_window_height,
        options.get( "fps", FPS_DEFAULT ),
        options.get( "vsync", VSYNC_DEFAULT ),
        options.get( "title", OVERLAY_WINDOW_TITLE_DEFAULT )
    );

    # Main rendering loop

    # Constants
    margin: int = options.get( "margin", MARGIN_DEFAULT );
    two_margin: int = margin * 2;
    font = rl.get_font_default();

    history_start_x: int = overlay_window_width // 2;

    # Animation controllers
    key_history_animation_controller = AnimationController( 0, 0, smoothstep, 1 );
    recent_keys_alpha_animation_controller = AnimationController( 0, 0, smoothstep, 1 );

    key_up_start_x: int = 0; # Persist the 
    while not rl.window_should_close():
        # Move & size window
        #left, top, right, bottom = win32gui.GetWindowRect( handle );
        left, top, right, bottom = get_window_pos( handle );
        overlay_window_width = right - left;
        history_start_x = overlay_window_width // 2;
        #target_window_height = bottom - top;
        rl.set_window_size( overlay_window_width, overlay_window_height );
        rl.set_window_position( left, bottom - overlay_window_height );

        rl.clear_background( overlay_clear_color );
        rl.begin_drawing();
        rl.draw_fps( 0, 0 );

        # TODO: support for changing these params at runtime may be added later
        icon_height: int = overlay_window_height - two_margin;
        half_icon_height = icon_height // 2;

        history_colour = [245, 245, 245, 255];

        key_history_lock.acquire(); # Lock the deques for rendering (block the event thread for a bit)

        # Begin by placing the cursor at the rightmost end
        draw_x: int = overlay_window_width - margin;

        # Render pressed keys
        for key in pressed_keys:
            if draw_x <= 0:
                break; # Next key is definitely off-screen

            w = max( icon_height, rl.measure_text( key, half_icon_height ) + two_margin );
            draw_x -= w;

            rl.draw_rectangle(
                draw_x, margin,
                w, icon_height,
                rl.RAYWHITE
            );
            rl.draw_text( key, draw_x + margin, margin + half_icon_height, half_icon_height, rl.BLACK );

            draw_x -= margin;

        # draw_x is now at the end of the pressed_keys block
        
        # Render recent keys
        draw_x = min( history_start_x, draw_x ); # Place the cursor as close to the key up block start as possible
        key_up_start_x = draw_x; # Remember the start X of the key up block (history + recent)
        for key, times_pressed in reversed( key_up_recent ):
            if draw_x < 0:
                break;

            if times_pressed > 1:
                # TODO: access glyph width of number character
                rl.draw_text( str( times_pressed ), draw_x - margin, margin + half_icon_height, half_icon_height // 2, history_colour );
            
            # TODO: animation

            w = max( icon_height, rl.measure_text( key, half_icon_height ) + two_margin ); # Width of box
            #total_width += w;
            draw_x -= w;

            rl.draw_rectangle(
                draw_x, margin,
                w, icon_height,
                [128, 128, 128, int( recent_keys_alpha_animation_controller.tick() )]
            );
            
            rl.draw_text( key, draw_x + margin, margin + half_icon_height, half_icon_height, history_colour );

            draw_x -= margin;

        # Render key history; animate its start offset
        # draw_x is now at the end of the recent_keys block
        
        # Scissor out the area of the recent_keys block and the pressed_keys block
        # This prevents key_history from covering recent_keys, without having to move the
        #   history rendering before the recent_keys rendering and make the draw_x pattern
        #   even more complicated
        rl.begin_scissor_mode( 0, 0, draw_x, overlay_window_height );

        if start_animation_flag[0]:
            # Set animation start and endpoints to the default start X and the target X (offset by th width of the recent keys)
            #print( "starting animation" )
            key_history_animation_controller.restart( key_up_start_x, draw_x );
            recent_keys_alpha_animation_controller.restart( 255, 50 );
            start_animation_flag[0] = False;

        # draw_x will be somewhere between the start and end of the recent_keys block
        draw_x = int( key_history_animation_controller.tick() );
        #print( f"{key_history_animation_controller.time=} {key_history_animation_controller.started=}" );
        for key, times_pressed in reversed( key_up_history ):
            if draw_x < 0:
                break;

            if times_pressed > 1:
                # TODO: access glyph width of number character
                rl.draw_text( str( times_pressed ), draw_x - margin, margin + half_icon_height, half_icon_height // 2, history_colour );

            w = max( icon_height, rl.measure_text( key, half_icon_height ) + two_margin ); # Width of box
            draw_x -= w;

            #print( f"{x=}, {margin=}, {w=}, {h=}, {history_colour=}" )

            rl.draw_rectangle_lines(
                draw_x, margin,
                w, icon_height,
                history_colour
            );
            # TODO: fix all the int casts
            rl.draw_text( key, draw_x + margin, margin + half_icon_height, half_icon_height, history_colour );

            draw_x -= margin;
            history_colour[3] = max( history_colour[3] // 2, HISTORY_MIN_ALPHA_DEFAULT );

        rl.end_scissor_mode();
        rl.end_drawing();

        # Merge recent keys into history once animation finishes
        if key_history_animation_controller.time >= 1:
            #log_info( "Merging" );
            # Merge the animation and history together if animation is complete
            # TODO: merge duplicate keys
            key_up_history.extend( key_up_recent );
            key_up_recent.clear();
            # Stop and reset the controller, so that the next frames will draw the combined array
            # at the original start position
            key_history_animation_controller.stop_and_reset();
            recent_keys_alpha_animation_controller.stop_and_reset();

        key_history_lock.release();


### ==================================================================

# if __name__ == "__main__":
#     import argparse, atexit;
    
#     parser = argparse.ArgumentParser(
#         prog="kpoverlay History Overlay",
#         description="Standalone history overlay",
#         epilog="(c) 2025 diblenderbenzene"
#     );
    
#     parser.add_argument( "-t", "--targetname" );
#     parser.add_argument( "-c", "--config" );

#     args = parser.parse_args();

#     handle = FindWindow( None, args.targetname );
    
#     atexit.register( cleanup );
#     run( handle, {} );
