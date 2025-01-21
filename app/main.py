from fastapi import FastAPI, HTTPException
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool
from sqlalchemy import create_engine
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Database connection
DATABASE_URL = "mysql+pymysql://root:2001@mysql:3306/testdb"
engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

# LangChain setup

llm = OpenAI(model="gpt-4", temperature=0, openai_api_key="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")

# Define prompt for summarization
prompt = PromptTemplate(
    input_variables=["data"],
    template=(
        "The following are details of suppliers for a specific product:\n\n{data}\n\n"
        "Please summarize this information concisely for the user."
    ),
)
summarization_chain = LLMChain(llm=llm, prompt=prompt)

# Query tool for database
query_tool = QuerySQLDataBaseTool(db=db)

# Pydantic model for input
class ProductRequest(BaseModel):
    product_name: str

# Helper function to query the database
def fetch_supplier_data(product_name: str):
    query = f"""
    SELECT suppliers.supplier_name, suppliers.contact_info
    FROM products
    JOIN product_supplier ON products.product_id = product_supplier.product_id
    JOIN suppliers ON suppliers.supplier_id = product_supplier.supplier_id
    WHERE products.product_name = '{product_name}';
    """
    return query_tool.run(query)

# Endpoint for querying supplier details
@app.post("/get-suppliers/")
async def get_suppliers(request: ProductRequest):
    product_name = request.product_name.strip()
    
    try:
        # Query database
        raw_data = fetch_supplier_data(product_name)
        if not raw_data:
            raise HTTPException(status_code=404, detail="No suppliers found for the specified product.")
        
        # Generate summary using LLM
        summary = summarization_chain.run({"data": raw_data})
        return {"product": product_name, "summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
