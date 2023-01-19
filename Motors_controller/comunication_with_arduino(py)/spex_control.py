import serial
import serial.tools.list_ports
from time import sleep


####################################
######### FUNCTIONS ################
####################################

def list_serial_ports():
    COM_list = serial.tools.list_ports.comports()
    #port.name
    #port.device
    #port.description
    #port.hwid
    return COM_list



def command2serial(ser, TXD: str, verbose=True, Fprint = print):
    '''
    Send a command to the serial port and return the response, waiting for the 'ok/n' or 'error: <type error> string.
    The function checks the correct echo of the port and the 'ok/n' terminating string, returning what is in between them.
    
            Parameters:
                ser (serial.Serial): Serial port object
                TXD (str): Command to send
                verbose (bool): Print the response or not
                Fprint (function): Function to print the response. Default is print.

            Returns:
                RXD (str): A list of responses from the serial port, without the echo line.
    '''

    # generate the command
    if verbose:
        Fprint('-> ', TXD)

    # send the command
    ser.write((TXD+'\n').encode('utf-8'))

    # check the echo
    RXD = ser.read_until().decode('utf-8')[:-1]
    if verbose:
        Fprint('<- ', RXD)
    if RXD != TXD:
        raise Exception('Connection error: echo does not match the command')
    
    # read the response
    RXD_list = []
    while RXD != 'ok' and RXD[:5] != 'error':
        RXD = ser.read_until().decode('utf-8')[:-1]
        if verbose:
            Fprint('<- ', RXD)
        RXD_list.append(RXD)

    
    return RXD_list


def connect_motors(verbose=True, Fprint = print):
    '''
    Connect to the spex motor controller.
    
            Parameters:
                verbose (bool): Print the response or not
                print_fun (function): Function to print the response. Default is print.

            Returns:
                ser (serial.Serial): Serial port object
    '''

    COM_list = list_serial_ports()
    find_port = False
    for port in COM_list:
        # you must change the permissions! : sudo chmod a+rw /dev/ttyUSB0
        Fprint("Trying "+ port.device + " ...")
        ser = serial.Serial(port=port.device, baudrate=115200, timeout=0.1)
        sleep(2)

        # empty the buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        # send the command
        ser.write('whoareyou\n'.encode('utf-8'))
        RXD = ['','','']
        RXD[0] = ser.read_until().decode('utf-8')[:-1]
        RXD[1] = ser.read_until().decode('utf-8')[:-1]
        RXD[2] = ser.read_until().decode('utf-8')[:-1]

        if RXD[0]=='whoareyou' and RXD[1]=='Spex motors micro-controller' and RXD[2]=='ok':
            find_port = True
            break
    
    if find_port:
        ser.timeout = None
        Fprint('-------------------------------------------')
        Fprint('Connected to the spex motor controller!')
        Fprint('port: ', ser.name)
        Fprint('description: ', port.description)
        Fprint('-------------------------------------------')
        #Fprint("Checking the status ...")
        #command2serial(ser, 'status', verbose=verbose, Fprint = Fprint)

        return motors(ser, verbose=verbose, Fprint = Fprint)
    
    else:
        Fprint('-------------------------------------------')
        Fprint('ERROR: Spex motor controller not found')
        Fprint('-------------------------------------------')
        return None






class motors:

    def __init__(self, port, verbose=True, Fprint = print):

        self.port = port
        self.verbose = verbose
        self.Fprint = Fprint

        if type(port) == serial.serialposix.Serial:
            self.ser = port
        elif type(port) == str:
        # you must change the permissions! : sudo chmod a+rw /dev/ttyUSB0
            self.ser = serial.Serial(port=port, baudrate=9600)
        
    def command(self, TXD: str, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        return command2serial(self.ser, TXD, verbose=verbose, Fprint = Fprint)

    def status(self, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = self.command('status', verbose=verbose, Fprint = Fprint)
        
        return 0
    
    def whoareyou(self, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = self.command('whoareyou', verbose=verbose, Fprint = Fprint)
        
        return RXD[0]
    
    def set_speed(self, motor: str, speed: int, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if motor!='spec' and motor!='filter':
            raise Exception("Type error: motor must be 'spec' or 'filter'")
        
        RXD = self.command('{} set_speed {}'.format(motor, speed), verbose=verbose, Fprint = Fprint)

        return 0
    
    def read_speed(self, motor: str, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if motor!='spec' and motor!='filter':
            raise Exception("Type error: motor must be 'spec' or 'filter'")
        
        RXD = self.command('{} read_speed'.format(motor), verbose=verbose, Fprint = Fprint)

        if RXD[-1]!='ok':
            raise Exception("Range error: speed out of range") 

        return int(RXD[0])

    def read_pos(self, motor: str, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if motor!='spec' and motor!='filter':
            raise Exception("Type error: motor must be 'spec' or 'filter'")
        
        RXD = self.command('{} read_pos'.format(motor), verbose=verbose, Fprint = Fprint)

        if RXD[1]=='ok':
            limit = 0
        elif RXD[1]=="error: clockwise limit reached":
            limit = 1
        elif RXD[1]=="error: counter-clockwise limit reached":
            limit = -1

        return int(RXD[0]), limit

    def init_pos(self, motor :str, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if motor!='spec' and motor!='filter':
            raise Exception("Type error: motor must be 'spec' or 'filter'")
        
        RXD = self.command('{} init_pos'.format(motor), verbose=verbose, Fprint = Fprint)

        return 0

    def goto(self, motor: str, pos:int, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if motor!='spec' and motor!='filter':
            raise Exception("Type error: motor must be 'spec' or 'filter'")
        
        RXD = self.command('{} goto {}'.format(motor, pos), verbose=verbose, Fprint = Fprint)

        if RXD[1]=='ok':
            limit = 0
        elif RXD[1]=="error: clockwise limit reached":
            limit = 1
        elif RXD[1]=="error: counter-clockwise limit reached":
            limit = -1

        return int(RXD[0]), limit

    def jump(self, motor: str, jump: int, verbose=None, Fprint = None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if motor!='spec' and motor!='filter':
            raise Exception("Type error: motor must be 'spec' or 'filter'")
        
        RXD = self.command('{} jump {}'.format(motor, jump), verbose=verbose, Fprint = Fprint)

        if RXD[1]=='ok':
            limit = 0
        elif RXD[1]=="error: clockwise limit reached":
            limit = 1
        elif RXD[1]=="error: counter-clockwise limit reached":
            limit = -1

        return int(RXD[0]), limit
    

    
