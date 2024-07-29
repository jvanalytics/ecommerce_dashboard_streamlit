import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pandasql as ps


# STREAMLIT Page setup ----------------------

st.set_page_config(layout="centered",
                   page_title="Ecommerce Analytics")


st.title(f"Ecommerce Analytics")


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


tab2, tab3 = st.tabs(['SQL 1', 'SQL 2'])

with tab2:
    st.subheader(
        "Query that displays number of users per day that only viewed products in their first session")

    query = """
    WITH first_sessions AS (
        SELECT user, MIN(session) AS first_session
        FROM df
        GROUP BY user
    ),
    first_session_products AS (
        SELECT df.*
        FROM df
        JOIN first_sessions
        ON df.user = first_sessions.user
        AND df.session = first_sessions.first_session
        WHERE df.page_type = 'product_page'
    ),
    next_sessions AS (
        SELECT DISTINCT df.user
        FROM df
        JOIN first_sessions
        ON df.user = first_sessions.user
        WHERE df.session != first_sessions.first_session
        AND df.page_type = 'product_page'
    ),
    users_only_first_session_products AS (
        SELECT first_session_products.user
        FROM first_session_products
        LEFT JOIN next_sessions
        ON first_session_products.user = next_sessions.user
        WHERE next_sessions.user IS NULL
    )

    SELECT 
        DATE(first_session_products.event_date) AS date,
        COUNT(DISTINCT first_session_products.user) AS non_returning_users
    FROM first_session_products
    JOIN users_only_first_session_products
    ON first_session_products.user = users_only_first_session_products.user
    GROUP BY date;

    """

    # Run SQL query on DataFrame
    first_query_result = ps.sqldf(query, locals())

    st.code(query, language="sql")

    st.subheader("1st query output")
    st.dataframe(first_query_result)


# second sql query


with tab3:
    st.subheader(
        "Query that will return any abnormal user behavior")

    st.markdown(
        """Here we are trying to analyze traffic outliers (abnormal session counts). 
        Ideally I would prefer to consider any traffic count that goes beyond a certain percentile (like 75th or 95th percentile).
        However the pandasql library uses SQLite and we cannot perform percentile calculation with it. 
        So in that case I made it a bit more interactive by calculating the average session count per user and calculate the abnormal values based on a user input multiplier that you can change.
        This query can also be adapted to detect abnormal event actions like add to cart or purchase or even session duration.
        """""
    )

    multiplier = st.slider("Select Multiplier to detect abnormal Session Count per User",
                           min_value=1.0, max_value=8.0, value=3.0, step=0.5)

    second_query = f"""
    WITH user_summary AS (
    SELECT
        user,
        COUNT(*) AS total_sessions,
        COUNT(DISTINCT page_type) AS page_types_visited
    FROM df
    GROUP BY user
    ),
    avg_values AS (
    SELECT
        AVG(total_sessions) AS avg_total_sessions
    FROM user_summary
    )

    SELECT
    user,
    total_sessions,
    page_types_visited,
    CASE
        WHEN total_sessions > {multiplier} * avg_values.avg_total_sessions THEN 'Abnormal Session Count'
        ELSE 'Normal'
    END AS abnormal_behavior
    FROM user_summary, avg_values
    LIMIT 30000 -- limited to 30K rows to be lighter on performance after dataframe creation
    """

    st.code(second_query, language="sql")

    # Run the SQL query on the DataFrame
    second_query_result = ps.sqldf(second_query, locals())

    st.subheader("2nd query output")

    st.button("Reset", type="primary")

    if st.button("Toggle Abnormal Only"):
        second_query_df = second_query_result[second_query_result['abnormal_behavior']
                                              == 'Abnormal Session Count']

        st.dataframe(second_query_df)

    else:
        st.dataframe(second_query_result)
