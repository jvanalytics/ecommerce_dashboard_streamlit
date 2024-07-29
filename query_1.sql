WITH first_sessions AS (
    SELECT user,
        MIN(session) AS first_session
    FROM sql_df
    GROUP BY user
),
first_session_products AS (
    SELECT sql_df.*
    FROM sql_df
        JOIN first_sessions ON sql_df.user = first_sessions.user
        AND sql_df.session = first_sessions.first_session
    WHERE sql_df.page_type = 'product_page'
),
next_sessions AS (
    SELECT DISTINCT sql_df.user
    FROM sql_df
        JOIN first_sessions ON sql_df.user = first_sessions.user
    WHERE sql_df.session != first_sessions.first_session
        AND sql_df.page_type = 'product_page'
),
users_only_first_session_products AS (
    SELECT first_session_products.user
    FROM first_session_products
        LEFT JOIN next_sessions ON first_session_products.user = next_sessions.user
    WHERE next_sessions.user IS NULL
)
SELECT DATE(first_session_products.event_date) AS date,
    COUNT(DISTINCT first_session_products.user) AS non_returning_users
FROM first_session_products
    JOIN users_only_first_session_products ON first_session_products.user = users_only_first_session_products.user
GROUP BY date;