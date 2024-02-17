from openai import OpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  model="mistralai/mixtral-8x7b-instruct",
  messages=[
    {
      "role": "user",
      "content": "Say this is a test",
    },
  ],
)
print(completion.choices[0].message.content)