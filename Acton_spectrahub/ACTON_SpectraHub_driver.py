import serial
import serial.tools.list_ports
from time import sleep



####################################
######### FUNCTIONS ################
####################################

def list_serial_ports():
    '''
    List all the serial ports available in the system.
    '''

    COM_list = serial.tools.list_ports.comports()
    #port.name
    #port.device
    #port.description
    #port.hwid
    return COM_list

def command2serial(ser, TXD, verbose=False, Fprint=print):
    '''
    Send a command to the serial port and return the response
    
            Parameters:
                TXD (str): Command to send
                verbose (bool): Print the response or not

            Returns:
                RXD (str): Response from the serial port
    '''

    # send the command
    ser.write((TXD+'\r').encode('utf-8'))
    if verbose:
        Fprint('-> ', TXD)

    # check the echo
    RXD = ser.read(len(TXD)).decode('utf-8')
    
    if RXD!=TXD:
        raise Exception('error: echo not reported')
    if verbose:
        Fprint('<- ', RXD)

    # read the response
    RXD = ser.read_until(expected=b'ok\r\n').decode('utf-8')

    RXD_list = RXD.split('\r\n')
    del RXD_list[-1]


    if RXD_list[-1][-2:]!='ok':
        raise Exception('error: ok not reported')

    # split by spaces and remove the empty strings
    for i in range(len(RXD_list)):
        splitted = RXD_list[i].split(' ')
        while ' ' in splitted:
            splitted.remove(' ')
        while '' in splitted:
            splitted.remove('')
        RXD_list[i] = splitted
    while [] in RXD_list:
        RXD_list.remove([])

    if verbose:
        for i in RXD_list:
            text = ''
            for j in i:
                text += j + ' '
            Fprint('<- ', text)

    

    return RXD_list

def connect_detector(verbose=True, Fprint = print):

    COM_list = serial.tools.list_ports.comports()
    find_port = False
    for port in COM_list:
        # you must change the permissions! : sudo chmod a+rw /dev/ttyUSB0
        if verbose:
            Fprint("Trying "+ port.device + " ...")
        ser = serial.Serial(port=port.device, baudrate=9600, timeout=0.5)
        sleep(2)

        # empty the buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        # send the command
        ser.write(b'?READOUT\r')
        RXD = ser.read_until(b'ok\r\n').decode('utf-8')[:-2].split(' ')
        
        if RXD[0]=='?READOUT' and RXD[2]=='ok':
            find_port = True
            break

    
    if find_port:
        ser.timeout = None
        if verbose:
            Fprint('--------------------------------------------------------')
            Fprint('Connected to SpectraHub detector (PMT) reader!')
            Fprint('port: ', ser.name)
            Fprint('description: ', port.description)
            Fprint('--------------------------------------------------------')
        return detector(ser, verbose=verbose, Fprint = Fprint)
    
    else:
        if verbose:
            Fprint('--------------------------------------------------------')
            Fprint('ERROR: SpectraHub detector (PMT) reader not found')
            Fprint('--------------------------------------------------------')
        return None


####################################
############### CLASSES ############
####################################

class detector:

    def __init__(self, port, verbose=True, Fprint=print):
       
        self.verbose = verbose
        self.Fprint = Fprint
        # you must change the permissions! : sudo chmod a+rw /dev/ttyUSB0
        if type(port) == serial.serialposix.Serial:
            self.ser = port
        elif type(port) == str:
        # you must change the permissions! : sudo chmod a+rw /dev/ttyUSB0
            self.ser = serial.Serial(port=port, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)
        
        # set the default values
        self.readout = 'I'
        self.set_readout(self.readout, verbose=verbose)
        self.polarity = 'UNI'
        self.set_polarity(self.polarity, verbose=verbose)
        self.itime = self.read_itime()   # ms
        self.range = self.read_range()   # V or A
        
       


    def command(self, TXD, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = command2serial(self.ser, TXD, verbose=verbose, Fprint=Fprint)
        return RXD

    def read(self, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = command2serial(self.ser, '.READ', verbose=verbose)

        counts = int(RXD[0][0])
        
        if self.range==0:
            I_fullscale = -2e-4/self.itime
            I = counts*I_fullscale/2**20
        if self.range==1:
            I_fullscale = -1e-4/self.itime
            I = counts*I_fullscale/2**20
        if self.range==2:
            I_fullscale = -4e-5/self.itime
            I = counts*I_fullscale/2**20
        if self.range==3:
            I_fullscale = -4e-6/self.itime
            I = counts*I_fullscale/2**20
    
        return I

    def range_info(self, verbose=True, Fprint=None):
        if Fprint is None:
            Fprint = self.Fprint
        
        print('-----------------------------')
        print('0: ' + 'fullscale [A] = -2e-4 A ms / itime[ms]')
        print('1: ' + 'fullscale [A] = -1e-4 A ms / itime[ms]')
        print('2: ' + 'fullscale [A] = -4e-5 A ms / itime[ms]')
        print('3: ' + 'fullscale [A] = -4e-6 A ms / itime[ms]')
        print()
        print('The ADC is a 20 bit ADC working in uni-polar mode, thus')
        print('I = counts * fullscale / 2^20')
        print('-----------------------------')
        return int(RXD[0][1])
    def set_readout(self, new_readout, verbose=None, Fprint=None):
        self.readout = new_readout

        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        if new_readout=='V' or new_readout=='Voltage' or new_readout=='voltage' or new_readout=='VOLTAGE':
            raise Exception('error: change of readout not allowed in this setup. If the harware is changed, this function can be used by modifing the source library.')
            RXD = command2serial(self.ser, 'VOLTAGE', verbose=verbose)
        if new_readout=='I' or new_readout=='Current' or new_readout=='current' or new_readout=='CURRENT':
            RXD = command2serial(self.ser, 'CURRENT', verbose=verbose)
        return int(RXD[0][1])

    def read_readout(self, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = command2serial(self.ser, '?READOUT', verbose=verbose)
        return RXD[0]

    def set_itime(self, new_itime, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        self.itime = new_itime
        RXD = command2serial(self.ser, f'{self.itime} ITIME', verbose=verbose)
        RXD[3][0] = 'final g'
        del RXD[3]
        del RXD[-1]
        return RXD
    
    def read_itime(self, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = command2serial(self.ser, '?ITIME', verbose=verbose)
        return int(RXD[0][0])

    def set_range(self, new_range, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        self.range = new_range
        RXD = command2serial(self.ser, f'{self.range} RANGE', verbose=verbose)
        del RXD[-1]
        return RXD

    def read_range(self, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        RXD = command2serial(self.ser, '?RANGE', verbose=verbose)
        return int(RXD[0][0])

    def set_polarity(self, new_polarity, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint
        
        self.polarity = new_polarity
        if new_polarity=='UNI' or new_polarity=='UNI-POLAR' or new_polarity=='uni' or new_polarity=='uni-polar' or new_polarity=='UNI-POLAR' or new_polarity=='UNI-POLAR':
            RXD = command2serial(self.ser, 'UNI-POLAR', verbose=verbose)
        if new_polarity=='BI' or new_polarity=='BI-POLAR' or new_polarity=='bi' or new_polarity=='bi-polar' or new_polarity=='BI-POLAR' or new_polarity=='BI-POLAR':
            raise Exception('error: change of polarity not allowed in this setup. If the harware is changed, this function can be used by modifing the source library.')
            RXD = command2serial(self.ser, 'BI-POLAR', verbose=verbose)

        del RXD[-1]
        return RXD

    def read_polarity(self, verbose=None, Fprint=None):
        if verbose is None:
            verbose = self.verbose
        if Fprint is None:
            Fprint = self.Fprint

        RXD = command2serial(self.ser, '?POLARITY', verbose=verbose)
        return RXD[0]

    def empty_buffer(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        return 0
        