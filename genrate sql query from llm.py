import os
from dotenv import load_dotenv
from google import genai
from sqlalchemy import create_engine, inspect

load_dotenv()


def get_db_schema():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # Connection String
    conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
    engine = create_engine(conn_str)
    inspector = inspect(engine)
    schema_text = ""
    
    for table_name in inspector.get_table_names():
        schema_text += f"\nTable: {table_name}\nColumns: "
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        schema_text += ", ".join(columns) + "\n"
    
    return schema_text

# 2. Gemini 
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def start_sql_bot(user_question,full_schema):  

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
                "system_instruction": (
                    "You are a SQL expert. Use the provided schema to write a SQL Server query. "
                    "Output ONLY the raw SQL code. No explanation, no formatting like ```sql."
                        )
                },
        contents=f"Database Schema:\n{full_schema}\n\nQuestion: {user_question}"
            )
            
    return response.text

def main ():
    print(" check datatbas and schema ...")
    full_schema = get_db_schema()
    print("Schema was successfully pulled")
    print ("\naske any question or exsist")

    while True:
        user_question = input("\naske")
        if user_question.lower() in ['exit', 'quit']:
            break
        try:
             result = start_sql_bot(user_question,full_schema)
             print(f"\ngeminai:\n{result}")
        except Exception as e:
            print(f"error  {e}")

if __name__ == "__main__":
    main()