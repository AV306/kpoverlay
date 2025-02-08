import inspect;

enable_debug = True;

def log_debug( msg: str ):
    if enable_debug:
        print( f"[{inspect.stack()[1].function} DEBUG] {msg}" );

def log_info( msg: str ):
    print( f"[{inspect.stack()[1].function} DEBUG] {msg}" );

def log_warn( msg: str ):
    print( f"[{inspect.stack()[1].function} WARN] {msg}" );

def log_error( msg: str ):
    print( f"[{inspect.stack()[1].function} ERROR] {msg}" );
