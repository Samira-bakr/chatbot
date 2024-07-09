from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
from openai import RateLimitError
import backoff

@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    response = openai.Completion.create(**kwargs)
    return response
llm = OpenAI(temperature=0,openai_api_key=OPENAI_API_KEY,max_retries=1)
# Here it is by default set to "AI"
conversation = ConversationChain(
    llm=llm, verbose=True, 
)
conversation.predict(input="Hi there!")