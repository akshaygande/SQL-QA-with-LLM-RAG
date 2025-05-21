import os
import getpass
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.chat_models import init_chat_model

# Database Configuration
DB_URI = "mysql+pymysql://root:Munna%402004@localhost:3306/final"
# DB_URI = "mysql+pymysql://root:Munna%402004@localhost:3306/schooldb"

# Initialize database
db = SQLDatabase.from_uri(DB_URI)

def get_schema_info(db):
    """Retrieve comprehensive schema information including foreign keys"""
    schema_info = []
    tables = db.get_usable_table_names()
    for table in tables:
        columns = db.run(f"DESCRIBE {table};")
        
        fk_query = f"""
            SELECT
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE
                TABLE_SCHEMA = DATABASE() AND
                TABLE_NAME = '{table}' AND
                REFERENCED_TABLE_NAME IS NOT NULL;
        """
        foreign_keys = db.run(fk_query)
        schema_entry = f"""
        Table: {table}
        Columns: {columns}
        Foreign Keys: {foreign_keys if foreign_keys else 'None'}
        """
        schema_info.append(schema_entry)
    return "\n".join(schema_info)

# Get schema info once at startup
schema_info = get_schema_info(db)

# Get Groq API key if not set
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")

# Create the system prompt template
system_prompt = """You are a MySQL expert. Generate efficient and accurate SQL queries using:
Schema Info:
{schema_info}
 
Only use the table_name, columns that are present in the schema info to generate query.
Generate clean SQL queries without any prefix like 'sql' or additional formatting.

Guidelines:
1. Use explicit JOINs instead of WHERE for relationships
2. Prefer EXISTS over IN for subqueries
3. Use table aliases (c for Course, s for Section, etc.)
4. Handle many-to-many via junction tables
5. Consider these key relationships:
   - Section connects Course (CourseID) ↔ Classrooms (RoomNumber) ↔ Buildings (BuildingID)
   - Faculty/Students/Interns → Person (PersonID)
   - Course → Textbook (TextbookISBN)
   - Section → Building + Classroom + Course + Person

Important: Return only the raw SQL query without any markdown formatting or prefixes.
Question: {question}
SQL Query:"""


summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that explains SQL query results in plain English.
    Given the original question, SQL query, and its results, provide a clear and concise summary of what the data shows.
    Focus on key insights and important numbers. Keep the explanation brief but informative."""),
    ("human", """
    Original Question: {question}
    SQL Query: {query}
    Results: {results}
    
    Please provide a clear summary of what this data shows:""")
])

# Create the summary chain

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}")
])
def generate_summary(question, query, results):
    """Generate a natural language summary of the query results"""
    return summary_chain.invoke({
        "question": question,
        "query": query,
        "results": results
    })
# Create prompt template


def clean_sql_query(query):
    """Clean and format SQL query by removing markdown and extra whitespace"""
    # Remove markdown SQL indicators
    query = query.replace("```sql", "").replace("```", "")
    # Remove 'sql' prefix if present
    query = query.replace("sql ", "")
    query = query.replace("\n"," ")
    # Clean up whitespace
    query = " ".join(query.split())
    return query.strip()

def execute_query(query):
    """Execute the SQL query and return results"""
    try:
        cleaned_query = clean_sql_query(query)
        if cleaned_query:
            return db.run(cleaned_query)
        return "No valid query to execute"
    except Exception as e:
        return f"Error executing query: {str(e)}"

# Create the chain with schema info
def generate_response(question):
    return chain.invoke({
        "question": question,
        "schema_info": schema_info
    })

chain = (
    prompt 
    | llm 
    | StrOutputParser()
)
summary_chain = (
    summary_prompt 
    | llm 
    | StrOutputParser()
)

# Streamlit UI
st.set_page_config(
    page_title="SQL Talk with MySQL",
    layout="wide",
)

st.title("SQL Talk with MySQL Database")
st.subheader("Powered by Groq LLM")

# Sample prompts
with st.expander("Sample prompts", expanded=True):
    st.write(
        """
        - List all buildings and their total classrooms?
        - Which building has the most classrooms?
        - Find the highest and lowest faculty salaries in each college?
        - How many faculty members are there per department?
        - Retrieve all faculty members along with the total number of sections they are teaching?
        """
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql_details" in message:
            with st.expander("SQL Query and Results"):
                st.markdown(message["sql_details"])

# Chat input and processing
if prompt := st.chat_input("Ask me about the database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Get LLM response with schema info
            llm_response = generate_response(prompt)
            
            # Clean and execute SQL query
            clean_query = clean_sql_query(llm_response)
            results = execute_query(clean_query)
            
            # Generate summary of results
            summary = generate_summary(prompt, clean_query, results)
            
            # Create response with query, results, and summary
            sql_details = f"""
            **Summary:**
            {summary}

            **SQL Query:**
            ```sql
            {clean_query}
            ```
            
            **Results:**
            ```
            {results}
            ```
            """
            
            # Display response
            message_placeholder.markdown(sql_details)
            
            # Add to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": sql_details,
                "sql_details": sql_details
            })

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })