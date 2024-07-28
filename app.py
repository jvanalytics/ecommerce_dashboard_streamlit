import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# STREAMLIT Page setup ----------------------

st.set_page_config(layout="wide",
                   page_title="PiwikPro Realtime Analytics")


st.title(f"Ecommerce Product Analytics")


st.sidebar.markdown(
    """

Looking at available data schema the Purchase Funnel can be defined by count the number of sessions or users per major step (action or page)

1. Total Traffic
2. Interest demonstration (page visit on listing page, product page or search listing page) - an user can add an item through any of these three page types
3. Add to Cart
4. Purchase
    
    
    """)

st.sidebar.text("Created by João Valente. Enjoy!")
st.sidebar.markdown(
    "[Linkedin](https://www.linkedin.com/in/joao-valente-analytics/)", unsafe_allow_html=True)
st.sidebar.markdown(
    "[Medium](https://medium.com/@jvanalytics)", unsafe_allow_html=True)
st.sidebar.markdown(
    "[Github](https://github.com/jvanalytics)", unsafe_allow_html=True)


# STREAMLIT Data


filepath = 'data_set_da_test.csv'

df = pd.read_csv(filepath)

total_sessions = df['session'].nunique()


interested_session_df = df[df['page_type'] != 'order_page']
interested_sessions = interested_session_df['session'].nunique()


add_to_cart_df = df[df['event_type'] == 'add_to_cart']
add_to_cart_sessions = add_to_cart_df['session'].nunique()


purchase_df = df[df['event_type'] == 'order']
purchase_sessions = purchase_df['session'].nunique()


session_cr = round(purchase_sessions/total_sessions*100, 2)

add_to_cart_rate = round(add_to_cart_sessions/total_sessions*100, 2)

cart_abandonment_rate = round(
    (add_to_cart_sessions-purchase_sessions)/add_to_cart_sessions*100, 2)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sessions", total_sessions)
    st.metric("Session Conversion Rate", f'{session_cr} %')


with col2:
    st.metric("Interested User Sessions", interested_sessions)
    st.metric("Add to Cart Rate", f'{add_to_cart_rate} %')


with col3:
    st.metric("Add to Cart Sessions", add_to_cart_sessions)
    st.metric("Cart Abandonment Rate", f'{cart_abandonment_rate} %')

with col4:
    st.metric("Purchase Sessions", purchase_sessions)


# Main Funnel visualization

stages = ['Total Sessions', 'Interested Sessions',
          'Add to Cart Sessions', 'Purchase Sessions']
values = [total_sessions, interested_sessions,
          add_to_cart_sessions, purchase_sessions]

fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textinfo="value+percent initial"
))


st.plotly_chart(fig)
