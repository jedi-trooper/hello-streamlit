import altair as alt
import pickle
import datetime
from icici import apification
from objects import create
import streamlit as st

api_key = "25$M3#O845r45lZ425Jj60&75*2Y5sa6"
api_secret = "d5EQ3W$X027972ns5@6U8q`2683716mS"
api_session = '22930328'

# Title for your app
st.markdown(
    """
    <h1 style='text-align: center; color: orange;'>ICICI API</h1>
    """,
    unsafe_allow_html=True
)


# Text input field for user to enter a name
appKey = st.text_input('APP Key:', api_key)
secretKey = st.text_input('Secret Key:', api_secret)
sessionKey = st.text_input('Session Key:', api_session, type="password")    

creds = {
    'appKey':appKey,
    'secretKey':secretKey,
    'sessionKey':sessionKey
}


# Define a function to activate the object
def activate_object():    
    with st.spinner(text='activating...'):
        client = apification(creds)
        st.session_state.client = client

        if client.api is not None:
            obj = client.get_object()
            details = client.user_details()        
            userID = details['userID']

            st.session_state.username = details['username']
            create(userID, obj)

            st.json(details)    
        else:
            st.text("INVALID CREDENTIALS")

        st.success('Done')    
        
        
# Button to activate the object
if st.button('Activate', type='primary'):
    activate_object()
    
if "client" in st.session_state:
    st.sidebar.text("Status : Active")
    st.sidebar.text(f"User :{st.session_state.username}")    
    
else:
    st.sidebar.text("Status : Deactive")
    
    

    
    
