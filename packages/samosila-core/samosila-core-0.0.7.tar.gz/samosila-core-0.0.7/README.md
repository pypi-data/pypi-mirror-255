# Samosila 


## Overview 

Samosila is my attempt to recreate an **OpenAI Compatible Server** for generating text, images, embeddings, and storing them in vector databases. It also includes a chat functionality. 

The server's request and responses are very similar to OpenAI's API with additional fields needed for different providers. It uses **Langchain** for the LLM part (Robust and powerful with callbacks) and provider SDKs for image generation and more.