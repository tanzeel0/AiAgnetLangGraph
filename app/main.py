from fastapi import FastAPI, HTTPException
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool
from sqlalchemy import create_engine
from pydantic import BaseModel
from langgraph.graph import Graph
from langgraph.prebuilt import ToolExecutor

# Initialize FastAPI app
app = FastAPI()

# Database connection (same as before)
DATABASE_URL = "mysql+pymysql://root:2001@localhost:3306/testdb"
engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

# LangChain setup (LLM and Prompt remain the same)
llm = OpenAI(model="gpt-4", temperature=0, openai_api_key="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")

prompt = PromptTemplate(
    input_variables=["data"],
    template=(
        "The following are details of suppliers for a specific product:\n\n{data}\n\n"
        "Please summarize this information concisely for the user."
    ),
)

# Query tool (same as before)
query_tool = QuerySQLDataBaseTool(db=db)
tools = [query_tool]
tool_executor = ToolExecutor(tools)

# LangGraph setup
workflow = Graph()

# Define nodes
def fetch_data(product_name: str):
    query = f"""
    SELECT suppliers.supplier_name, suppliers.contact_info
    FROM products
    JOIN product_supplier ON products.product_id = product_supplier.product_id
    JOIN suppliers ON suppliers.supplier_id = product_supplier.supplier_id
    WHERE products.product_name = '{product_name}';
    """
    return {"data": tool_executor.invoke(query)}

def summarize_data(data: dict):
    if not data["data"]:
        return {"summary": "No suppliers found."} # Handle no results case here
    summary = llm(prompt.format(**data))
    return {"summary": summary}

# Add nodes to graph
workflow.add_node("fetch_data", fetch_data)
workflow.add_node("summarize_data", summarize_data)

# Set edges
workflow.add_edge("fetch_data", "summarize_data")

# Compile the graph
compiled_workflow = workflow.compile()

# Pydantic model for input (same as before)
class ProductRequest(BaseModel):
    product_name: str

# Endpoint for querying supplier details
@app.post("/get-suppliers/")
async def get_suppliers(request: ProductRequest):
    product_name = request.product_name.strip()

    try:
        # Run the LangGraph workflow
        result = compiled_workflow.invoke(product_name)
        return {"product": product_name, "summary": result["summarize_data"]["summary"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
