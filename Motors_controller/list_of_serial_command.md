# List of serial commands to comunicate with the motors microcontroller (Arduino nano)
-boud rate: 115200
-Data bits: 8
-Parity: None
-Stop bits: 1
-Flow control: None

Each command must be termiated with a new line character (`\n`). The microcontroller respond with a series of lines terminated with a new line character (`\n`). The first line is an echo of the command. The final line contains the string 'ok' if the command was executed correctly or 'error', folowed by ': <error type>' if the command was not executed correctly.
Here, the possibilities are:

- 'error: unknown command': the command is not recognized
- 'error: clockwise limit reached': the motor reached the clockwise limit
- 'error: counter-clockwise limit reached': the motor reached the counter-clockwise limit
- 'error: speed out of range': the speed is not in the range [0, MaxSpeed]

When the microcontroller is busy, it has the built in led on. When the microcontroller is ready to receive a new command, the led is off.


## Global commands

### `status`
Returns 'ok' if everithing goes fine, just to check if the connection is working.
es:  `status`
out: `status`
     `ok`

### 'whoareyou'
Returns an identification string of the microcontroller, for auto-detection porpuses.
es:  `whoareyou`
out: `whoareyou`
     `Spex motors micro-controller`
     `ok`

## Control motors commands commands
To control the motors you must pass a set of arguments to the microcontroller. The first identifies the motor on wich you are acting:
- 'spec': the spectrograph motor
- 'filter': the filter motor
The second is the command, and the third is the argument (if present) of the command. The arguments are separated by a space character (` `). The commands are:

### '<spec/filter> set_speed <speed>'
Set the speed of the spectrometer/filter motor. The speed is an unsigned integer, measured in steps per milliseconds.
es:  `filter set_speed 50`
out: `filter set_speed 50`
     `ok`

### '<spec/filter> read_speed'
Returns the current speed of the spectrometer/filter motor.
es:  `filter read_speed`
out: `filter read_speed`
     `50`
     `ok`

### '<spec/filter> read_pos'
Returns the current position of the spectrometer/filter motor. This absolute position is setted at the swich on of the microcontroller to 0. To keep track of the position, the microcontroller counts the number of steps of the motor. The position is an integer, measured in steps.
es:  `filter read_pos`
out: `filter read_pos`
     `38`
     `ok`

### '<spec/filter> init_pos'
Set the current position of the spectrometer/filter motor to 0. This command is useful to reset the position of the motor.
es:  `filter init_pos`
out: `filter init_pos`
     `ok`

### '<spec/filter> goto <position>'
Move the spectrometer/filter motor to the specified position. Returns also the final position of the motor.
es:  `filter goto 50`
out: `filter goto 50`
     `50`
     `ok`
If the motor bumps into the limit switch, the motor stops. The microcontroller returns the final position, and returns 'error: clockwise limit reached' or 'error: counter-clockwise limit reached'.
es:  `filter goto 50`
out: `filter goto 50`
     `38`
     `error: clockwise limit reached`



### '<spec/filter> jump <steps>'
Move the spectrometer/filter motor of the specified number of steps. Returns also the final position of the motor. The direction of the movement is determined by the sign of the number of steps. If the number of steps is positive, the motor moves clockwise, if the number of steps is negative, the motor moves counter-clockwise.
es:  `filter jump 50`
out: `filter jump 50`
     `88`
     `ok`
If the motor bumps into the limit switch, the motor stops. The microcontroller returns the final position, and returns 'error: clockwise limit reached' or 'error: counter-clockwise limit reached'.
es:  `filter jump -100`
out: `filter jump -100`
     `38`
     `error: counter-clockwise limit reached`