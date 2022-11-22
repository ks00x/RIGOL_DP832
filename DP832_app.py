'''
A simple streamlit app to control a Rigol DP832 Power supply
pip install pyvisa pyvisa-py
conda install -c conda-forge pyvisa pyvisa-py
tested with streamlit 1.14
'''
import streamlit as st
import pandas as pd
import time 
import DP832

session = st.session_state
st.set_page_config(page_icon='📉')

st.cache
def get_urls():    
    session.urls = DP832.get_visa_resources()    

st.cache
def init():  
    session.dp = DP832.DP832(session.url)
    for k in range(3): # initialize the channel control widgets
        session[f'spv_ch{k+1}'] = session.dp.get_voltage(k+1)
        session[f'spc_ch{k+1}'] = session.dp.get_current(k+1)
        session[f'on_ch{k+1}'] = session.dp.get_output(k+1)
        
with st.sidebar:
    with st.form(key='select_urls'):
        get_urls()
        item = st.selectbox('visa resources',session.urls)
        if st.form_submit_button('connect'):
            session.url = item #session.urls[item]  
            if 'dp' in session:
                init.clear()  
                del session.dp                
            init()
    if 'dp' in session: # only visible if connected
        if st.button('disconnect'):
            del session.dp            
            del session.df                 
            st.experimental_rerun() # manual restart of the script        
        if st.button('download csv',help='csv file with date-time name will be stored in the scripts folder'):
            import datetime 
            f = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.csv")
            session.df.to_csv(f,sep=' ')
        st.selectbox('plot channel',(1,2,3),key='plotchan')
        st.number_input('points to plot',value=500,key='plotlen')
        st.number_input('plot delay [s]',value=2,key='plotdelay')
                            
if 'dp' in session: # only run the following if we are connected to the instrument
    def set_v(k):
        v = float(session[f'spv_ch{k+1}'])
        session.dp.set_voltage(k+1,v)
        time.sleep(0.3)
    def set_c(k):
        v = float(session[f'spc_ch{k+1}'])
        session.dp.set_current(k+1,v)
        time.sleep(0.3)
    def set_out(k):
        v = session[f'on_ch{k+1}']
        session.dp.set_output(k+1,v)
        time.sleep(0.3)
    
    disp_area = st.empty()
    ctrls = st.columns(3)    
    plot1 = st.empty()
    plot2 = st.empty()
    plot3 = st.empty()
    st.write(session.dp.idn)  

    for k in range(3): # control widgets                
        ctrls[k].checkbox('Output ON',key=f'on_ch{k+1}',on_change=set_out,args=(k,))
        ctrls[k].number_input('setpoint V',key=f'spv_ch{k+1}',on_change=set_v,args=(k,))
        ctrls[k].number_input('setpoint A',key=f'spc_ch{k+1}',on_change=set_c,args=(k,))
    
    if 'df' not in session: # init the pandas df for storage of measurement history
        col_names = ['time']
        for k in range(3): 
            col_names += [f'CH{k+1}_V',f'CH{k+1}_I',f'CH{k+1}_P']           
        session.df = pd.DataFrame(columns=col_names)
        session.ctr = 0 # loop / data row counter
    dt = 0.
    while True: # main loop            
        data = [time.time()]  
        for k in range(3): # update meter readings and df table
            chn = disp_area.columns(3)
            x = session.dp.measure_all(k+1)            
            data += x
            chn[k].write(f'### Channnel {k+1}')
            chn[k].metric('Voltage [V]',x[0])
            chn[k].metric('Current [A]',x[1])
            chn[k].metric('Power [W]',x[2])
        session.df.loc[session.ctr] = data
        session.ctr += 1
        if time.time() - dt >= session.plotdelay:
            plot2.line_chart(session.df.tail(session.plotlen),y=f'CH{session.plotchan}_I')
            plot1.line_chart(session.df.tail(session.plotlen),y=f'CH{session.plotchan}_V')
            plot3.line_chart(session.df.tail(session.plotlen),y=f'CH{session.plotchan}_P')
            dt = time.time()
        time.sleep(0.5)
