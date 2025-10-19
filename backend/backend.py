from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI  # ✓ Correct
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
courses_collection = client.get_collection("courses")
requirements_collection = client.get_collection("requirements")

# Initialize Gemini LLM - UPDATED MODEL NAME
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# In-memory user storage
users = {}

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

class ChatResponse(BaseModel):
    response: str

class UserProfile(BaseModel):
    major: str = "CS"
    completed_courses: list[str] = []
    current_quarter: str = "Winter 2025"

@app.get("/")
async def root():
    return {
        "status": "Academic Advisor API Running (Gemini)",
        "courses_loaded": courses_collection.count(),
        "requirements_loaded": requirements_collection.count()
    }

@app.post("/set-profile")
async def set_profile(user_id: str, profile: UserProfile):
    """Set user's academic profile"""
    users[user_id] = {
        "major": profile.major,
        "completed_courses": profile.completed_courses,
        "current_quarter": profile.current_quarter
    }
    return {"status": "success", "profile": users[user_id]}

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    return users.get(user_id, {
        "major": "CS",
        "completed_courses": [],
        "current_quarter": "Winter 2025"
    })

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - answers student questions"""
    
    # Get user info
    user_info = users.get(request.user_id, {
        "major": "CS",
        "completed_courses": [],
        "current_quarter": "Winter 2025"
    })
    
    # Search courses relevant to question
    course_results = courses_collection.query(
        query_texts=[request.message],
        n_results=5
    )
    
    # Search requirements relevant to question
    req_results = requirements_collection.query(
        query_texts=[request.message],
        n_results=3
    )
    
    # Format context
    course_context = "\n\n".join(course_results['documents'][0]) if course_results['documents'] else "No relevant courses found."
    req_context = "\n\n".join(req_results['documents'][0]) if req_results['documents'] else "No relevant requirements found."
    
    # Create prompt
    prompt = ChatPromptTemplate.from_template("""
You are a helpful academic advisor at the University of Washington helping a CS student.

Student Information:
- Major: {major}
- Completed Courses: {completed_courses}
- Current Quarter: {current_quarter}

Relevant Courses from Database:
{course_context}

Relevant Degree Requirements:
{requirements_context}

Student Question: {question}

Instructions:
- Answer specifically based on the course and requirement information provided
- Include course codes, schedules, and prerequisites when relevant
- Be helpful and encouraging
- If you don't have enough information, say so
- Keep answers concise but complete

Answer:
    """)
    
    chain = prompt | llm
    
    # Get LLM response
    response = chain.invoke({
        "major": user_info["major"],
        "completed_courses": ", ".join(user_info["completed_courses"]) if user_info["completed_courses"] else "None listed",
        "current_quarter": user_info["current_quarter"],
        "course_context": course_context,
        "requirements_context": req_context,
        "question": request.message
    })
    
    return ChatResponse(response=response.content)

@app.get("/search-courses")
async def search_courses(query: str, n_results: int = 10):
    """Search for courses"""
    results = courses_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return {
        "query": query,
        "results": [
            {
                "id": results['ids'][0][i],
                "text": results['documents'][0][i][:200] + "...",
                "metadata": results['metadatas'][0][i]
            }
            for i in range(len(results['ids'][0]))
        ]
    }

@app.get("/requirements")
async def get_requirements():
    """Get all CS requirements"""
    results = requirements_collection.query(
        query_texts=["CS major requirements"],
        n_results=20
    )
    
    return {
        "requirements": [
            {
                "id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            }
            for i in range(len(results['ids'][0]))
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)