PI = 3.14159;
TWO_PI = 6.28319;




class AnimationController:
    """Generic time manager for an animation."""
    def __init__( self, start_value, end_value, interp_func, tick_rate ):
        self.start_value = start_value;
        self.end_value = end_value;
        self.interpolation_func = interp_func;
        self.tick_rate = tick_rate;

        self.delta = end_value - start_value;
        self.time = 0;
        self.started = False;

    def restart( self, start_value, end_value ) -> None:
        self.start_value = start_value;
        self.end_value = end_value;
        self.delta = self.end_value - self.start_value
        self.time = 0;
        self.started = True;

    def stop_and_reset( self ) -> None:
        self.time = 0;
        self.started = False;

    def tick( self, delta_time=1/60 ) -> float:
        """
        Increment the animation's progres by tick_rate * delta_time.
        delta_time must be in seconds.
        """
        value = self.start_value + self.interpolation_func( self.time ) * self.delta;
        
        # Increment time only if in progress
        if self.started:
            self.time += self.tick_rate * delta_time;
            if self.time >= 1:
                self.time = 1;
                self.started = False;

        return value;

    def done( self ) -> bool:
        return self.time >= 1;

# class Animation:
#     """Generic animation: supply your own start/end values and interpolation function."""
#     def __init__( self, start_value: any, end_value: any, interpolation_func: Callable[[int], int] ):
#         self.start_value = start_value;
#         self.end_value = end_value;
#         self.delta = end_value - start_value;
#         self.interpolation_func = interpolation_func;

#     def get( self, value ):
#         return self.start_value + self.interpolation_func( value ) * self.delta;


# Interpolation functions ==============================

def linear_interpolate( v ) -> float:
    return 0 if v < 0 else v if v < 1 else 1;

def smoothstep( x ) -> float:
    return 0 if x <= 0 else 3*pow( x, 2 ) - 2*pow( x, 3 ) if x < 1 else 1;

def sinusodial( x ) -> float:
    return 0 if x <= 0 else 0.5 - cos( PI * x ) if x < 1 else 1;

def mid_step( x ) -> int:
    return 0 if x <= 0.5 else 1;
