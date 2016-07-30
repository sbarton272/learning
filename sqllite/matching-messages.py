import sqlite3 as sql
import pandas as pd

# Create new database
SQLITE_FILE_NAME = 'practice.sqlite'
conn = sql.connect(SQLITE_FILE_NAME)

# Populate table
df_messages = pd.DataFrame({
    'sender_id' : [1, 2, 3, 1, 2, 3, 4],
    'receiver_id' : [2, 3, 3, 3, 1, 1, 1],
    'transmit_time' : [0, 1, 6, 3, 4, 5, 2]},
    index = range(0,7))
df_messages.index.name = 'message_id'
print df_messages

# Write to SQL
MESSAGES_TABLE_NAME = 'messages'
cur = conn.cursor()
cur.execute('drop table if exists %s' % MESSAGES_TABLE_NAME)
df_messages.to_sql(MESSAGES_TABLE_NAME, conn)

# Practice SQL
print 'Transmit > 3'
query_str = 'SELECT * FROM %s WHERE `transmit_time` > 3 ORDER BY `sender_id`' % MESSAGES_TABLE_NAME
print pd.read_sql_query(query_str, conn)

# Look for all messages where there was no response
print 'Sender 1'
query_str = """
SELECT *
FROM %s 
WHERE `sender_id` = 1 
ORDER BY `transmit_time`
""" % MESSAGES_TABLE_NAME
print pd.read_sql_query(query_str, conn)

print 'Receiver 1'
query_str = """
SELECT *
FROM %s 
WHERE `receiver_id` = 1 
ORDER BY `transmit_time`
""" % MESSAGES_TABLE_NAME
print pd.read_sql_query(query_str, conn)

print 'Count Message by Sender'
query_str = """
SELECT sender_id, COUNT(message_id) AS cnt_send
FROM %s 
GROUP BY sender_id
ORDER BY sender_id
""" % MESSAGES_TABLE_NAME
print pd.read_sql_query(query_str, conn)

print 'Count Message by Receiver'
query_str = """
SELECT receiver_id, COUNT(message_id) AS cnt_send
FROM %s 
GROUP BY receiver_id
ORDER BY receiver_id
""" % MESSAGES_TABLE_NAME
print pd.read_sql_query(query_str, conn)

print 'Count All Responses'
query_str = """
SELECT snd_t.sender_id, COUNT(rec_t.sender_id) AS resp_cnt
FROM (SELECT DISTINCT sender_id FROM %s) AS snd_t
LEFT JOIN %s AS rec_t ON snd_t.sender_id = rec_t.receiver_id
GROUP BY snd_t.sender_id
ORDER BY snd_t.sender_id
""" % (MESSAGES_TABLE_NAME, MESSAGES_TABLE_NAME)
print pd.read_sql_query(query_str, conn)

print 'All Messages and Responses'
query_str = """
SELECT snd_t.message_id AS msg_id, snd_t.transmit_time < rec_t.transmit_time AS valid
FROM %s AS snd_t
LEFT JOIN %s AS rec_t ON snd_t.sender_id = rec_t.receiver_id
ORDER BY snd_t.message_id
""" % (MESSAGES_TABLE_NAME, MESSAGES_TABLE_NAME)
print pd.read_sql_query(query_str, conn)

print 'Count Future Responses Per Message'
query_str = """
SELECT msg_id, IFNULL(SUM(valid),0) AS cnt_valid_resp
FROM(
    SELECT snd_t.message_id AS msg_id, snd_t.transmit_time < rec_t.transmit_time AS valid
    FROM %s AS snd_t
    LEFT JOIN %s AS rec_t ON snd_t.sender_id = rec_t.receiver_id
    ORDER BY snd_t.message_id
)
GROUP BY msg_id
ORDER BY msg_id
""" % (MESSAGES_TABLE_NAME, MESSAGES_TABLE_NAME)
print pd.read_sql_query(query_str, conn)

print 'Count Messages with no Response'
query_str = """
SELECT msg_id
FROM (
    SELECT msg_id, IFNULL(SUM(valid),0) AS cnt_valid_resp
    FROM(
        SELECT snd_t.message_id AS msg_id, snd_t.transmit_time < rec_t.transmit_time AS valid
        FROM %s AS snd_t
        LEFT JOIN %s AS rec_t ON snd_t.sender_id = rec_t.receiver_id
        ORDER BY snd_t.message_id
    )
    GROUP BY msg_id
)
WHERE cnt_valid_resp = 0
ORDER BY msg_id
""" % (MESSAGES_TABLE_NAME, MESSAGES_TABLE_NAME)
print pd.read_sql_query(query_str, conn)