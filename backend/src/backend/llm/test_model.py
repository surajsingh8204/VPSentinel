from backend.llm.models import get_gemini_primary , get_groq_primary

#llm=get_gemini_primary()

llm=get_groq_primary()
response=llm.invoke("top 5 ideas for final year major project as btech cse student in 2026 give in proper indentation and spacing remove * and / symbol")

print(response.text)








