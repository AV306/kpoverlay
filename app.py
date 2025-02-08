from history_overlay import run, cleanup;
import atexit, argparse, win32gui;

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="kpoverlay History Overlay",
        description="Standalone history overlay",
        epilog="(c) 2025 diblenderbenzene"
    );
    
    parser.add_argument( "-t", "--targetname" );
    parser.add_argument( "-c", "--config" );

    args = parser.parse_args();

    handle = win32gui.FindWindow( None, args.targetname );
    
    atexit.register( cleanup );
    run( handle, {"fps": -1, "vsync": False} );
