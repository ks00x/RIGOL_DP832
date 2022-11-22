import pyvisa as visa

bindict = dict(YES=True,NO=False,ON=True,OFF=False)


def get_visa_resources():
    'returns a list of available visa resource urls'
    rm = visa.ResourceManager()
    return rm.list_resources()

class DP832:

    def __init__(self, visa_adr):                
        rm = visa.ResourceManager()        
        self.address = visa_adr
        self.device = rm.open_resource(visa_adr)
        self.idn = self.device.query('*IDN?')
        # print('connect to ',self.idn)
        
    def channel_status(self,chan:int)->dict:
        'returns status of channel <chan> (1,2,3) as a dict (mode,on,ocp,ovp,track)'       
        d = {}
        ret = self.device.query(f':OUTPUT:MODE? CH{chan}')
        d['mode'] = ret[:-1]
        ret = self.device.query(f':OUTPUT:OCP:QUES? CH{chan}')
        d['ocp'] = bindict[ret[:-1]]
        ret = self.device.query(f':OUTPUT:OVP:QUES? CH{chan}')
        d['ovp'] = bindict[ret[:-1]]
        ret = self.device.query(f':OUTPUT:STAT? CH{chan}')
        d['on'] = bindict[ret[:-1]]
        ret = self.device.query(f':OUTPUT:TRACK? CH{chan}')
        d['track'] = bindict[ret[:-1]]
        return d

    def set_output(self,chan:int,state:bool=False):
        'switches the output on or off of channel <chan> (1,2,3)'                
        self.device.write(f'OUTP CH{chan},{"ON" if state else "OFF"}')        

    def get_output(self,chan:int)->bool:
        'gets the output status '
        ret = self.device.query(f':OUTPUT:STAT? CH{chan}')
        return bindict[ret[:-1]]

    def set_voltage(self,chan:int,voltage:float = 0.):
        'sets the setpoint voltage of channel <chan> (1,2,3)'                
        self.device.write(f'SOURCE{chan}:VOLT {voltage}')        

    def get_voltage(self,chan:int)->float:
        'returns the setpoint voltage of channel <chan> (1,2,3)'                
        ret = self.device.query(f'SOURCE{chan}:VOLT?')
        return float(ret)

    def set_current(self,chan:int,voltage:float = 0.):
        'sets the setpoint current of channel <chan> (1,2,3)'                
        self.device.write(f'SOURCE{chan}:CURR {voltage}')        

    def get_current(self,chan:int)->float:
        'returns the setpoint current of channel <chan> (1,2,3)'                
        ret = self.device.query(f'SOURCE{chan}:CURR?')
        return float(ret)
    
    
    def measure_voltage(self, chan:int) -> float:  
        'returns the measured voltage(V) of channel <chan> (1,2,3)'
        volt = self.device.query(f':MEAS:VOLT? CH{chan}')
        return float(volt)        

    def measure_current(self, chan:int) -> float:  
        'returns the measured current (A) of channel <chan> (1,2,3)'
        volt = self.device.query(f':MEAS:CURR? CH{chan}')
        return float(volt)        
    
    def measure_power(self, chan:int) -> float:  
        'returns the measured power (W) of channel <chan> (1,2,3)'
        volt = self.device.query(f':MEAS:POWE? CH{chan}')        
        return float(volt)        
        
    def measure_all(self, chan:int) -> float:  
        'returns a tuple (V,I,P) of channel <chan> (1,2,3)'
        ret = self.device.query(f':MEAS:ALL? CH{chan}')        
        return tuple(float(x) for x in ret.split(','))   


    def set_ocp(self,chan:int,state:bool=False,val:float=3):
        'sets the ocp state and value of channel <chan> (1,2,3)'  
        self.device.write(f'OUTP:OCP CH{chan},{"ON" if state else "OFF"}')         
        self.device.write(f'OUTP:OCP:VAL CH{chan},{val}')         

    def get_ocp(self,chan:int)->tuple:
        'returns the ocp state and value of channel <chan> (1,2,3)'                
        ret1 = self.device.query(f'OUTP:OCP:VAL? CH{chan}')
        ret2 = self.device.query(f'OUTP:OCP? CH{chan}')
        return bindict[ret2[:-1]] , float(ret1)                 

    def set_ovp(self,chan:int,state:bool=False,val:float=3):
        'sets the ovp state and value of channel <chan> (1,2,3)'  
        self.device.write(f'OUTP:OVP CH{chan},{"ON" if state else "OFF"}')         
        self.device.write(f'OUTP:OVP:VAL CH{chan},{val}')         

    def get_ovp(self,chan:int)->tuple:
        'returns the ovp state and value of channel <chan> (1,2,3)'                
        ret1 = self.device.query(f'OUTP:OVP:VAL? CH{chan}')
        ret2 = self.device.query(f'OUTP:OVP? CH{chan}')
        return bindict[ret2[:-1]] , float(ret1)     

    def clear_overp(self,chan:int=1):
        'clears ovp and ocp status of channel'
        self.device.write(f'OUTP:OVP:CLEAR CH{chan}')         
        self.device.write(f'OUTP:OCP:CLEAR CH{chan}')         
    
    def __del__(self):
        self.device.close()
        ''



if __name__ == "__main__":

    rm = visa.ResourceManager()
    instrument_list = rm.list_resources()
    print(instrument_list)

    dp = DP832('TCPIP0::192.168.1.5::inst0::INSTR')
    

    for k in range(3):
        print(f'ch{k+1} = {dp.measure_all(k+1)}')

    dp.set_output(1,True)
    print(dp.channel_status(1))
    
    dp.set_voltage(1,9.5)
    print(dp.get_voltage(1))

    dp.set_current(1,0.2)
    print(dp.get_current(1))

    dp.set_ocp(1,True,2)
    print(dp.get_ocp(1))

    dp.set_ovp(1,True,28)
    print(dp.get_ovp(1))
    
    dp.set_output(2,True)
    print(dp.channel_status(2))
    
    dp.set_voltage(2,1.1)
    print(dp.get_voltage(2))