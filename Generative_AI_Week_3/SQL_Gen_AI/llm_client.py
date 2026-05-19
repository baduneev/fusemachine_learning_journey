# llm_client.py
# यो file LLM/Groq client setup गर्न र prompt पठाएर response लिन प्रयोग हुन्छ


# os module import gareko
# Environment variables read garna use huncha
import os


# dotenv bata load_dotenv import gareko
# .env file vitra ko variables load garna use huncha
from dotenv import load_dotenv


# groq package bata Groq client import gareko
# Yo Groq API sanga communicate garna use huncha
from groq import Groq


# .env file load gareko
# Example .env:
# GROQ_API_KEY=your_api_key_here
# GROQ_MODEL=llama-3.1-8b-instant
load_dotenv()


# Groq client create gareko
# api_key .env file bata read gareko
# यो client use garera LLM lai request पठाइन्छ
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# कुन model use गर्ने define gareko
# यदि .env मा GROQ_MODEL छैन भने default "llama-3.1-8b-instant" use हुन्छ
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# LLM lai prompt पठाउने function
# prompt: str means input prompt string format ma huncha
# return type str means LLM response text return garcha
def call_llm(prompt: str) -> str:

    # Groq chat completion API call gareko
    # यो LLM lai messages पठाएर answer generate garna लगाउँछ
    response = client.chat.completions.create(

        # कुन LLM model use गर्ने specify gareko
        model=MODEL,

        # messages list ma system instruction ra user prompt पठाइन्छ
        messages=[
            {
                # system role le LLM ko behavior/personality define गर्छ
                "role": "system",

                # LLM lai Text-to-SQL expert jasari काम गर्न instruction दिएको
                "content": "You are an expert PostgreSQL Text-to-SQL assistant."
            },
            {
                # user role ma actual prompt पठाइन्छ
                "role": "user",

                # Function मा आएको prompt LLM lai पठाएको
                "content": prompt
            }
        ],

        # temperature=0 means output deterministic/consistent बनाउने
        # Text-to-SQL जस्तो task मा random answer भन्दा stable answer राम्रो हुन्छ
        temperature=0
    )

    # LLM response bata generated text निकालेर return gareko
    # choices[0] means first response option
    # message.content means actual answer text
    return response.choices[0].message.content