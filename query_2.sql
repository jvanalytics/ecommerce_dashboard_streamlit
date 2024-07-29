WITH user_summary AS (
    SELECT user,
        COUNT(*) AS total_sessions,
        COUNT(DISTINCT page_type) AS page_types_visited
    FROM sql_df
    GROUP BY user
),
avg_values AS (
    SELECT AVG(total_sessions) AS avg_total_sessions
    FROM user_summary
)
SELECT user,
    total_sessions,
    page_types_visited,
    CASE
        WHEN total_sessions > 3.0 * avg_values.avg_total_sessions THEN 'Abnormal Session Count'
        ELSE 'Normal'
    END AS abnormal_behavior
FROM user_summary,
    avg_values