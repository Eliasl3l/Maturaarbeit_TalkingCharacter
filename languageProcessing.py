import openai
openai.api_key = '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'  # Replace with your OpenAI API key
language = 'en'

def get_chatgpt_response(query):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=query,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7
    )

    return response.choices[0].text.strip()
#return response.choices[0].text.strip()
print(get_chatgpt_response("how are your virtual circuits doing Mr. super smart?"))