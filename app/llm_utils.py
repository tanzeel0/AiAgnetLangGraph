from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

llm = OpenAI(model="gpt-4", temperature=0)

# Prompt for summarization
prompt = PromptTemplate(
    input_variables=["data"],
    template=(
        "The following are details of suppliers for a specific product:\n\n{data}\n\n"
        "Please summarize this information concisely for the user."
    ),
)
summarization_chain = LLMChain(llm=llm, prompt=prompt)

def generate_summary(data: str):
    return summarization_chain.run({"data": data})
