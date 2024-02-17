from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
    model="huggingfaceh4/zephyr-7b-beta",
  messages=[
    {
      "role": "user",
      "content": "Say this is a test",
    },
  ],
)
print(completion.choices[0].message.content)

