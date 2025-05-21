# SQL QA with LLM + RAG

A Streamlit-based application that enables natural language querying over structured SQL databases using a combination of Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs). This project allows users to interact with a SQL database via plain English questions, receiving SQL answers and explanations powered by state-of-the-art language models.

## 🔍 Features

* 🧠 Natural Language to SQL Conversion
* 📊 Query execution over a real SQL database
* 🔄 RAG integration for schema understanding and enhanced contextual awareness
* ⚡ Streamlit front-end for an interactive user experience
* 🧪 Notebook-based development (`SQL_qa_llm_rag.ipynb`) for iterative testing
* 📦 Modular script (`SQL_talkapp_grog.py`) for app deployment

## 🛠️ Tech Stack

* Python
* Streamlit
* LangChain
* Transformers (HuggingFace)
* SQLCoder (or compatible LLM)
* MySQL (or any SQL-compliant DB)
* FAISS (for RAG vector search)

## 📁 Project Structure

```
├── SQL_qa_llm_rag.ipynb       # Jupyter notebook for developing and testing QA pipeline
├── SQL_talkapp_grog.py        # Streamlit app for production UI
├── requirements.txt           # (Optional) Python dependencies
└── README.md                  # Project overview and instructions
```

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* MySQL server running with accessible schema
* API key or local model access for LLMs (e.g., SQLCoder)

### Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/sql-qa-llm-rag.git
   cd sql-qa-llm-rag
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Update database and model configuration in the script or notebook as needed.

### Running the App

```bash
streamlit run SQL_talkapp_grog.py
```

### Using the Notebook

Open `SQL_qa_llm_rag.ipynb` in JupyterLab or VS Code to test and explore the functionality step-by-step.

## ✨ Example Use Case

> **Question:** “Which customers have made more than 5 purchases last month?”

> **Response:**
>
> ```sql
> SELECT customer_name FROM orders WHERE purchase_date BETWEEN '2024-04-01' AND '2024-04-30' GROUP BY customer_name HAVING COUNT(*) > 5;
> ```

## 🧠 How It Works

1. **Schema Ingestion**: Metadata from SQL tables is parsed and embedded using a vector database.
2. **RAG Workflow**: The user's natural language query is matched against schema vectors to enrich the prompt.
3. **LLM Inference**: A large language model (like SQLCoder) generates an appropriate SQL query.
4. **Execution**: The generated SQL is run against the database and results are displayed.

## 📌 TODO

* [ ] Add authentication for app access
* [ ] Integrate more robust error handling
* [ ] Support for multiple DB engines
* [ ] Improve result visualizations (charts/tables)

## 📄 License

MIT License

