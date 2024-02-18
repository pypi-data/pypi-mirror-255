#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : generativeai
# @Time         : 2023/12/14 13:32
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://github.com/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb

from meutils.pipe import *


import google.generativeai as genai


# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("What is the meaning of life?")
response.prompt_feedback
response.candidates
response = model.generate_content("What is the meaning of life?", stream=True)
for chunk in response:
    print(chunk.text)
    print("_" * 80)


# model = genai.GenerativeModel('gemini-pro-vision')
# response = model.generate_content(img)
# response = model.generate_content(["Write a short, engaging blog post based on this picture. It should include a description of the meal in the photo and talk about my journey meal prepping.", img], stream=True)
# response.resolve()

#
# """
# At the command line, only need to run once to install the package via pip:
#
# $ pip install google-generativeai
# """
#
# import google.generativeai as genai
#
# genai.configure(api_key="YOUR_API_KEY")
#
# # Set up the model
# generation_config = {
#   "temperature": 0.9,
#   "top_p": 1,
#   "top_k": 1,
#   "max_output_tokens": 2048,
# }
#
# safety_settings = [
#   {
#     "category": "HARM_CATEGORY_HARASSMENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_HATE_SPEECH",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   }
# ]
#
# model = genai.GenerativeModel(model_name="gemini-pro",
#                               generation_config=generation_config,
#                               safety_settings=safety_settings)
#
# prompt_parts = [
#   "周树人暴打鲁迅",
# ]
#
# response = model.generate_content(prompt_parts)
# print(response.text)
