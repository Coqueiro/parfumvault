import google.generativeai as genai


def prompt_gemini(api_key, prompt):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Please summarise this document: ...')

    print(response.text)