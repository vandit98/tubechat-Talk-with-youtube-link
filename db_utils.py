import os
# from dotenv import load_dotenv
import psycopg2
import json
import traceback



host = os.getenv("host")
database = os.getenv("mysql_database")
user = os.getenv("mysql_user")
password = os.getenv("mysql_password")
port = os.getenv("mysql_port")

  # Database connection parameters
db_params = {
    "dbname": database,
    "user": user,
    "password": password,
    "host": host,
    "port": port,
}

def connect_to_database(db_params):
    try:
      
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # You can perform database operations here using the cursor
        # For example, you can execute SQL queries like this:
        # cursor.execute("SELECT * FROM your_table")
        # result = cursor.fetchall()
        # print(result)

        # Close the cursor and the database connection when done
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)



def create_video_data_table(db_params):
    try:
        # Database connection parameters

        # Establish a connection to the database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        check_table_sql = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'tubechatai'
        )
        """
        
        cursor.execute(check_table_sql)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("Table 'tubechatai' already exists.")
        else:
        # SQL statement to create the table
            create_table_sql = """
            CREATE TABLE tubechatai (
                youtube_video_id VARCHAR(20) PRIMARY KEY,
                video_data JSONB NOT NULL
            );
            """

            # Execute the SQL statement to create the table
            cursor.execute(create_table_sql)

            # Commit the changes and close the cursor and connection
            connection.commit()
            print("Table 'video_data' created successfully.")
        
        
        cursor.close()
        connection.close()

      

    except (Exception, psycopg2.Error) as error:
        print("Error creating table:", error)


def insert_video_data(result_dict):
    try:
        # Database connection parameters
       
        # Establish a connection to the database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        insert_sql = """
        INSERT INTO tubechatai (youtube_video_id, video_data)
        VALUES (%s, %s::jsonb)  -- Cast result_dict as JSONB
        """

        youtube_video_id = result_dict["id"]

        # Execute the insert statement with the provided data
        cursor.execute(insert_sql, (youtube_video_id, json.dumps(result_dict)))

        # Commit the changes to the database
        connection.commit()

        print(f"Data for video with ID '{youtube_video_id}' inserted successfully!")

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        print("Data inserted successfully.")

    except (Exception, psycopg2.Error) as error:
        print("Error inserting data:", error)






def print_all_data():
    try:
        # Database connection parameters
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Fetch all data from the 'tubechatai' table
        fetch_all_data_sql = """
        SELECT * FROM tubechatai
        """

        cursor.execute(fetch_all_data_sql)

        # Fetch all the rows
        rows = cursor.fetchall()
        print(rows)

        # if rows:
        #     for row in rows:
        #         youtube_video_id, video_data_json = row
        #         video_data = json.loads(video_data_json)
        #         print(f"Youtube Video ID: {youtube_video_id}")
        #         print(json.dumps(video_data, indent=4))  # Pretty-print the JSON data
        #         print("\n---\n")  # Separating each record with a line

        # else:
        #     print("No data found in the 'tubechatai' table.")

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data:", error)





def delete_all_data_from_table(table_name, db_params):
    try:
        # Establish a connection to the database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # SQL statement to delete all data from the specified table
        delete_sql = f"DELETE FROM {table_name}"

        # Execute the delete statement
        cursor.execute(delete_sql)

        # Commit the changes to the database
        connection.commit()

        print(f"All data deleted from table '{table_name}'.")

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Error deleting data from table '{table_name}':", error)

def fetch_video_data_by_id(youtube_video_id):
    try:
        # Database connection parameters
       
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Fetch the video_data for the specified youtube_video_id
        fetch_sql = """
        SELECT video_data
        FROM tubechatai
        WHERE youtube_video_id = %s
        """

        # Execute the query with the provided youtube_video_id
        cursor.execute(fetch_sql, (youtube_video_id,))

        # Fetch the result
        result = cursor.fetchone()

        if result:
            # The result is already in JSONB format, so no need to parse it
            video_data = result[0]
            return video_data
        else:
            print(f"No data found for youtube_video_id '{youtube_video_id}'")
            return None

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data:", error)
        return None
    



# Call the function to create the table
# if __name__ == "__main__":
#     # insert_video_data(result_dict)
    # if fetch_video_data_by_id(youtube_video_id="YDmXhlfEDv1"):
        # print(fetch_video_data_by_id(youtube_video_id="YDmXhlfEDv0"))
#     # print_all_data()
#     # delete_all_data_from_table(table_name="tubechatai", db_params=db_params)
    

