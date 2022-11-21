'''
A simple streamlit app to control a Rigol DP832 Power supply
pip install pyvisa pyvisa-py
conda install -c conda-forge pyvisa pyvisa-py
'''

import streamlit as st
import pandas as pd
import pyvisa as visa
import time 
from DP832 import DP832

session = st.session_state

st.cache
def get_urls():
    rm = visa.ResourceManager()
    session.urls = rm.list_resources()

st.cache
def init():  
    session.dp = DP832(session.url)
    for k in range(3):
        session[f'spv_ch{k+1}'] = session.dp.get_voltage(k+1)
        session[f'spc_ch{k+1}'] = session.dp.get_current(k+1)
        session[f'on_ch{k+1}'] = session.dp.get_output(k+1)
    return session.dp , True
    
with st.sidebar:
    with st.form(key='select_urls'):
        get_urls()
        item = st.selectbox('visa resources',session.urls)
        if st.form_submit_button('connect'):
            session.url = item #session.urls[item]  
            if 'connected' in session:
                init.clear()  
                del session.dp
                del session.connected
            session.dp,session.connected = init()
    if 'connected' in session:
        if st.button('disconnect'):
            del session.dp
            del session.connected   
            del session.df     
            #init.clear()  # clear the singleton status of init() -> run next time on connect!
            st.experimental_rerun() # manual restart of the script        
        if st.button('donwload csv'):
            import datetime 
            f = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.csv")
            session.df.to_csv(f,sep=' ')
            

                 
if 'connected' in session:
    def set_v(k):
        v = float(session[f'spv_ch{k+1}'])
        session.dp.set_voltage(k+1,v)
    def set_c(k):
        v = float(session[f'spc_ch{k+1}'])
        session.dp.set_current(k+1,v)
    def set_out(k):
        v = session[f'on_ch{k+1}']
        session.dp.set_output(k+1,v)
        time.sleep(0.2)
    
    
    disp_area = st.empty()
    ctrls = st.columns(3)
    st.selectbox('plot channel',(1,2,3),key='plotchan')
    plot1 = st.empty()
    plot2 = st.empty()
    plot3 = st.empty()

    for k in range(3):                 
        ctrls[k].checkbox('Output ON',key=f'on_ch{k+1}',on_change=set_out,args=(k,))
        ctrls[k].number_input('setpoint V',key=f'spv_ch{k+1}',on_change=set_v,args=(k,))
        ctrls[k].number_input('setpoint A',key=f'spc_ch{k+1}',on_change=set_c,args=(k,))

    st.write(session.dp.idn)  

    if 'df' not in session:
        col_names = ['time']
        for k in range(3): 
            col_names += [f'CH{k+1}_V',f'CH{k+1}_I',f'CH{k+1}_P']           
        session.df = pd.DataFrame(columns=col_names)
        session.ctr = 0 # loop / data row counter
            
    while True:                
        data = [time.time()]  
        for k in range(3):
            chn = disp_area.columns(3)
            x = session.dp.measure_all(k+1)            
            data += x
            chn[k].write(f'### Channnel {k+1}')
            chn[k].metric('Voltage [V]',x[0])
            chn[k].metric('Current [A]',x[1])
            chn[k].metric('Power [W]',x[2])
        session.df.loc[session.ctr] = data
        plot1.line_chart(session.df.tail(500),y=f'CH{session.plotchan}_V')
        plot2.line_chart(session.df.tail(500),y=f'CH{session.plotchan}_I')
        plot3.line_chart(session.df.tail(500),y=f'CH{session.plotchan}_P')
        time.sleep(1)
        session.ctr += 1


#st.write(session)