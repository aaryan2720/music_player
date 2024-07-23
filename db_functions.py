import os 
import sqlite3

database_dir = os.path.join(os.getcwd(), '.dbs')
app_database = os.path.join(database_dir, 'app_db.db')

#create a db
def create_tables(table_name: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (song TEXT)""")
    connection.commit()
    connection.close()


#add a song to db table 
def add_songs_to_database_table (song:str, table:str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f""" INSERT INTO {table} VALUES (?)""", (song,))
    connection.commit()
    connection.close()

#delete song from db 
def delete_songs_from_db_table(song:str ,table:str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(
        f""" 
        DELETE FROM {table} 
        WHERE ROWID = (SELECT MIN(ROWID) FROM {table} WHERE song = "{song}");
        """
    )
    connection.commit()
    connection.close()

def delete_all_songs_from_db_table(table:str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(
        f"""DELETE FROM {table}"""
    )
    connection.commit()
    connection.close()

#fetch song from db 
def fetch_all_songs_from_db(table:str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f""" SELECT song FROM {table}""")
    song_data = cursor.fetchall()
    data = [song [0] for song in song_data]
    connection.commit()
    connection.close()

    return data

# get all tables in db 
def get_playlist_tables():
    try:
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM sqlite_master WHERE type = 'table';""")
        table_names = cursor.fetchall()
        tables = [table_name[1] for table_name in table_names]  # Fix the typo here
        
        return tables
    except sqlite3.Error as e:
        print(f"Error getting table names: {e}")
    finally:
        connection.close()

# delete a database table 
def delete_db_table(table:str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f""" DROP TABLE {table}""")
    connection.commit()
    connection.close()