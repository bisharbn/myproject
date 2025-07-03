import openai

client = OpenAI()
 completion = openai.ChatCompletion.create(
  
client.images.generate(
  model="dall-e-3",
  prompt="A cute baby sea otter",
  n=1,
  size="1024x1024"
)
