import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pandasql as ps


# STREAMLIT Page setup ----------------------

st.set_page_config(layout="centered",
                   page_title="Ecommerce Analytics")


st.title(f"Ecommerce Analytics")


st.sidebar.markdown(
    """

Looking at available data schema the Purchase Funnel can be defined by count the number of sessions or users per major step (action or page)

1. Total Traffic
2. Interest demonstration (User shows interest through a page visit on listing page, product page or search listing page) 
3. Add to Cart
4. Purchase
    """)

st.sidebar.divider()


# User input for page type
page_type = st.sidebar.radio(
    'Filter Funnel, metrics and insights by Page Type',
    (None, 'Search Listing Page', 'Listing Page', 'Product Page'),
    format_func=lambda x: 'Overall' if x is None else x,
    horizontal=True
)

st.sidebar.divider()


user_scope = st.sidebar.radio(
    'Select if you want to see User Scope or session scope metrics. Note: Insights are predominantly made over sessions',
    ('Session-scope', 'User-scope'),
    horizontal=True
)


if user_scope == 'Session-scope':
    scope = 'session'

elif user_scope == 'User-scope':
    scope = 'user'


st.sidebar.divider()


st.sidebar.markdown(
    """
Main Remarks on additional data request:
- Apparently product column is only filled when add_to_cart is. It lacks purchase and product pageview events. As there are also 1.37 products added to cart per session, it does not allow for 1:1 product funnel analysis
- Product Impression per page type would also help understand how to optimize search and category listing results
- Additional information on product (category, price,additional specs) would allow for additional aggregation options
- Information on Traffic sources (to understand better traffic intent and impact of marketing actions on data)

    """)


st.sidebar.divider()


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

sql_df = df  # use for sql exercises

total_sessions = df[scope].nunique()


interested_session_df = df[df['page_type'] != 'order_page']
interested_sessions = interested_session_df[scope].nunique()

add_to_cart_df = df[df['event_type'] == 'add_to_cart']
add_to_cart_sessions = add_to_cart_df[scope].nunique()


purchase_df = df[df['event_type'] == 'order']
purchase_sessions = purchase_df[scope].nunique()


# funnel metrics

# 1st page type visited in each session
df['event_date'] = pd.to_datetime(df['event_date'])
df_sorted = df.sort_values(by=[scope, 'event_date'])
first_page_type_df = df_sorted.groupby(scope).first().reset_index()[
    [scope, 'page_type']]
df_first = df.merge(first_page_type_df, on=scope,
                    how='left', suffixes=('', '_first'))


# 2nd is the funnel function
def funnel_merge_df_type(df, page_type):

    total_type_sessions = total_sessions

    if page_type == 'Search Listing Page':
        first_search_listing_df = df[df['page_type_first']
                                     == 'search_listing_page']
        interested_type_sessions = first_search_listing_df[scope].nunique()

        first_search_listing_atc_df = df[(df['page_type_first'] == 'search_listing_page') & (
            df['event_type'] == 'add_to_cart')]
        atc_type_sessions = first_search_listing_atc_df[scope].nunique()

        purchase_type_sessions = first_search_listing_atc_df.merge(
            purchase_df, on=scope, how='inner')[scope].nunique()

    elif page_type == 'Listing Page':
        first_listing_df = df[df['page_type_first'] == 'listing_page']
        interested_type_sessions = first_listing_df[scope].nunique()

        first_listing_atc_df = df[(df['page_type_first'] == 'listing_page') & (
            df['event_type'] == 'add_to_cart')]
        atc_type_sessions = first_listing_atc_df[scope].nunique()

        purchase_type_sessions = first_listing_atc_df.merge(
            purchase_df, on=scope, how='inner')[scope].nunique()

    elif page_type == 'Product Page':
        first_product_page_df = df[df['page_type_first'] == 'product_page']
        interested_type_sessions = first_product_page_df[scope].nunique()

        first_product_page_atc_df = df[(df['page_type_first'] == 'product_page') & (
            df['event_type'] == 'add_to_cart')]
        atc_type_sessions = first_product_page_atc_df[scope].nunique()

        purchase_type_sessions = first_product_page_atc_df.merge(
            purchase_df, on=scope, how='inner')[scope].nunique()

    elif page_type is None:
        interested_type_sessions = interested_sessions
        atc_type_sessions = add_to_cart_sessions
        purchase_type_sessions = purchase_sessions

    else:
        raise ValueError(f"Unknown page type: {page_type}")

    return pd.Series({
        'sessions': total_type_sessions,
        'interested_sessions': interested_type_sessions,
        'add_to_cart_sessions': atc_type_sessions,
        'purchase_sessions': purchase_type_sessions
    })


# metrics per page_type
metrics = funnel_merge_df_type(df_first, page_type)

if page_type != None:

    interested_sessions = metrics['interested_sessions']
    add_to_cart_sessions = metrics['add_to_cart_sessions']
    purchase_sessions = metrics['purchase_sessions']

session_cr = round(purchase_sessions/interested_sessions*100, 2)

add_to_cart_rate = round(add_to_cart_sessions/interested_sessions*100, 2)


cart_abandonment_rate = round(
    (add_to_cart_sessions-purchase_sessions)/add_to_cart_sessions*100, 2)


tab1, tab2, tab3 = st.tabs(['Ecommerce Funnel', 'SQL 1', 'SQL 2'])

with tab1:

    # Funnel Analysis per Page Type

    st.subheader("Insights")

    if page_type == None:
        st.markdown(
            r"""
        Almost 100% of result in some but only 3% result in add to cart. However it has a very high overall cart conversion rate of 71.6% which indicates good product and shopping experience after adding to cart.

    """
        )
    elif page_type == "Search Listing Page":
        st.markdown(
            r"""
        Only 4% of sessions result in a user making first a session. Also, only 6.8% of those add a product to cart which indicates search might need to be improved or experiment giving it higher visibility when a user accesses the website/app.
    """
        )

    elif page_type == "Listing Page":
        st.markdown(
            r"""
        Users access first the Listing Page in 52% of sessions which should indicate that menu and category structures and visibility should be good.
        However, considering that users can add products through the listing page,less that 1% actually do it.
        Most likely, users will prefer to go to the Product Page to know more about the products before adding it. Curious that this does not happen the same way in Search Listing Page.
    """
        )

    elif page_type == "Product Page":
        st.markdown(
            r"""
        Users access Product Page 48% of sessions, which is also a good indicator of its easy discovery.
        It is also the main way of adding products to the cart (3%) and then purchase (1%).
    """
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(f"{scope.capitalize()}s (Overall | Interested)",
                  interested_sessions)
        st.metric(f"Purchase {scope.capitalize()}s", purchase_sessions)

    with col2:
        st.metric("Add to Cart Rate", f'{add_to_cart_rate} %')
        st.metric("Conversion Rate (Overall | Interested)",
                  f'{session_cr} %')

    with col3:
        st.metric(f"Add to Cart {scope.capitalize()}s",
                  add_to_cart_sessions)
        st.metric("Cart Abandonment Rate", f'{cart_abandonment_rate} %')

    st.divider()

    st.subheader('Funnel Visualization by First Type page visited')

    # Plotly funnel chart
    stages = ['Total Sessions', 'Interested Sessions',
              'Add to Cart Sessions', 'Purchase Sessions']
    values = [metrics['sessions'], metrics['interested_sessions'],
              metrics['add_to_cart_sessions'], metrics['purchase_sessions']]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial"
    ))

    fig.update_layout(title="Funnel Visualization")

    st.plotly_chart(fig)

    st.divider()

    st.subheader("Top 50 Products Added to Cart")
    # Calculate the number of unique products added to the cart per product

    df_product_overall_top_atc = df_first[df_first['event_type'] == 'add_to_cart'].groupby(
        'product')[scope].nunique().reset_index(name=f'Add to Cart {scope.capitalize()}s')

    df_product_pageview_top_atc = df_first[(df_first['event_type'] == 'add_to_cart') & (df_first['page_type_first'] == 'product_page')].groupby(
        'product')[scope].nunique().reset_index(name=f'Product Page Add to Cart {scope.capitalize()}s')

    df_product_listing_top_atc = df_first[(df_first['event_type'] == 'add_to_cart') & (df_first['page_type_first'] == 'listing_page')].groupby(
        'product')[scope].nunique().reset_index(name=f'Listing Page Add to Cart {scope.capitalize()}s')

    df_product_search_listing_atc = df_first[(df_first['event_type'] == 'add_to_cart') & (df_first['page_type_first'] == 'search_listing_page')].groupby(
        'product')[scope].nunique().reset_index(name=f'Search Listing Page Add to Cart {scope.capitalize()}s')

    merged_product_df = df_product_overall_top_atc.merge(
        df_product_pageview_top_atc, on='product', how='outer'

    ).merge(
        df_product_listing_top_atc, on='product', how='outer'

    ).merge(
        df_product_search_listing_atc, on='product', how='outer'
    )

    df['product'] = df['product'].astype('string')

    top_50_products = merged_product_df.sort_values(
        by=merged_product_df.columns[1], ascending=False).head(50)

    st.dataframe(top_50_products)


# second part of exercise (SQL Queries)

# ensure datetime format
sql_df['event_date'] = pd.to_datetime(sql_df['event_date'])


with tab2:
    st.subheader(
        "Query that displays number of users per day that only viewed products in their first session")

    query = """
    WITH first_sessions AS (
        SELECT user, MIN(session) AS first_session
        FROM sql_df
        GROUP BY user
    ),
    first_session_products AS (
        SELECT sql_df.*
        FROM sql_df
        JOIN first_sessions
        ON sql_df.user = first_sessions.user
        AND sql_df.session = first_sessions.first_session
        WHERE sql_df.page_type = 'product_page'
    ),
    next_sessions AS (
        SELECT DISTINCT sql_df.user
        FROM sql_df
        JOIN first_sessions
        ON sql_df.user = first_sessions.user
        WHERE sql_df.session != first_sessions.first_session
        AND sql_df.page_type = 'product_page'
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
    FROM sql_df
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
    LIMIT 100000 -- limited to 100k rows to be lighter after dataframe creation
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
