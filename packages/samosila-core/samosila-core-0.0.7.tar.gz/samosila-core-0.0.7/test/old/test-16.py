# import marvin
# from marvin import ai_classifier
# from enum import Enum

# marvin.settings.azure_openai.api_base = "http://127.0.0.1:8080"
# marvin.settings.llm_model = "azure_openai/Mistral-7B-OpenOrca"


# @ai_classifier # type: ignore
# class AppRoute(Enum):
#     """Represents distinct routes command bar for a different application"""

#     USER_PROFILE = "/user-profile"
#     SEARCH = "/search"
#     NOTIFICATIONS = "/notifications"
#     SETTINGS = "/settings"
#     HELP = "/help"
#     CHAT = "/chat"
#     DOCS = "/docs"
#     PROJECTS = "/projects"
#     WORKSPACES = "/workspaces"


# res = AppRoute("update my name")

# print(res)
# # AppRoute.USER_PROFILE


from openai import OpenAI
from pydantic import BaseModel
import openai
import instructor

# Enables `response_model`
client = instructor.patch(openai. OpenAI(
    base_url="http://127.0.0.1:8080",    
))
client.base_url = "http://127.0.0.1:8080"

class UserDetail(BaseModel):
    name: str
    age: int


user = client.chat.completions.create(
    model="Open-Orca/Mistral-7B-OpenOrca",
    response_model=UserDetail,
    messages=[
        {"role": "user", "content": "Extract Jason is 25 years old"},
    ]
)

assert isinstance(user, UserDetail)
assert user.name == "Jason"
assert user.age == 25

print(user)