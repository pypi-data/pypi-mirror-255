from langchain.chat_models import ChatGooglePalm
from langchain.prompts import ChatPromptTemplate
import google.auth

chat = ChatGooglePalm(
    google_api_key="AIzaSyDRNmS5Px7LvSXDA5rLbrfTrLRQFCyBW74",
) # type: ignore

system = "You are a helpful assistant who translate English to French"
human = "Translate this sentence from English to French. I love programming."
prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", human)])
messages = prompt.format_messages()


print(chat(messages))

