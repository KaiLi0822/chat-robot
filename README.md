Customer Service Robot based on LangChain  
https://www.langchain.com/
---
Project Structure:  
- main.py: Entry file
- answerQuestion.py: 
  - Using LangChain and LLM to generate answer
- ./tools/sensitiveCheck：
  - Sensitive words detection based on sensitive word list
- ./tools/classify
  - based on spaCy model, classify question into 5 types 
- ./tools/qaDatabase
  - Based on the type, search history data and get the most relevant QA 