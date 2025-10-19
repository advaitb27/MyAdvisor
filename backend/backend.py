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

# Default user profile for Nandini
DEFAULT_USER_PROFILE = {
    "name": "Nandini",
    "student_id": "2365887",
    "major": "Statistics (Data Science) and Computer Science (Double Major)",
    "class_standing": "Junior",
    "current_quarter": "Autumn 2025",
    "cumulative_gpa": 3.38,
    "total_credits": 126,

    "completed_courses": [
        # AP Credits
        "CHEM 142", "CHEM 152", "CSE 121", "ECON 200", "ECON 201",
        "MATH 124", "MATH 125", "STAT 290",

        # Autumn 2023
        "CSE 122", "CSE 190", "INFO 103", "MATH 126",

        # Winter 2024
        "CSE 123", "ENGL 131", "MATH 208",

        # Spring 2024
        "CSE 311", "CSE 331", "LING 269",

        # Autumn 2024
        "ARCH 350", "CSE 332", "PSYCH 210",

        # Winter 2025 (Dean's List)
        "CSE 312", "CSE 351", "CSE 391", "STAT 311", "STAT 394",

        # Spring 2025
        "CSE 333", "CSE 421", "CSE 490", "MATH 224", "MUSIC 116",

        # Summer 2025
        "ART H 273"
    ],

    "current_courses": [
        "ENGL 288", "STAT 302", "STAT 341", "CSE 473"
    ],

    "academic_highlights": [
        "Dean's List (Winter 2025)",
        "Strong performance in probability and statistics (4.0 in STAT 394)",
        "Completed core CS requirements: CSE 311, 312, 331, 332, 333, 351, 421",
        "Completed Statistics core: STAT 311, 394"
    ],

    "interests": "Double major in Statistics (Data Science) and Computer Science, with diverse interests in linguistics, architecture, psychology, music theory, and art history"
}

# In-memory user storage
users = {
    "default": DEFAULT_USER_PROFILE
}

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
    return users.get(user_id, DEFAULT_USER_PROFILE)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - answers student questions"""

    # Get user info (defaults to Nandini's profile)
    user_info = users.get(request.user_id, DEFAULT_USER_PROFILE)
    
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
You are a helpful academic advisor at the University of Washington helping {name}.

Student Profile:
- Name: {name}
- Major: {major}
- Class Standing: {class_standing}
- Current Quarter: {current_quarter}
- Cumulative GPA: {cumulative_gpa}
- Total Credits Earned: {total_credits}

Academic Highlights:
{academic_highlights}

Completed Courses ({num_completed} courses):
{completed_courses}

Currently Enrolled:
{current_courses}

Interests & Background:
{interests}

Relevant Courses from Database:
{course_context}

Relevant Degree Requirements:
{requirements_context}

Student Question: {question}

Instructions:
- Address the student by name ({name})
- Be conversational and friendly, like a helpful advisor who knows the student well
- Consider their completed courses when making recommendations (they've already taken these!)
- Consider their double major in both Statistics/Data Science AND Computer Science
- Reference their academic achievements (Dean's List, strong GPA in probability)
- Include course codes, schedules, and prerequisites when relevant
- Make personalized recommendations based on their interests and background
- Be encouraging and supportive
- If recommending courses, check prerequisites against their completed courses
- Keep answers concise but complete

Answer:
    """)
    
    chain = prompt | llm
    
    # Get LLM response
    response = chain.invoke({
        "name": user_info.get("name", "Student"),
        "major": user_info.get("major", "CS"),
        "class_standing": user_info.get("class_standing", "Junior"),
        "current_quarter": user_info.get("current_quarter", "Autumn 2025"),
        "cumulative_gpa": user_info.get("cumulative_gpa", "N/A"),
        "total_credits": user_info.get("total_credits", "N/A"),
        "academic_highlights": "\n".join(f"- {h}" for h in user_info.get("academic_highlights", [])),
        "num_completed": len(user_info.get("completed_courses", [])),
        "completed_courses": ", ".join(user_info.get("completed_courses", [])) if user_info.get("completed_courses") else "None listed",
        "current_courses": ", ".join(user_info.get("current_courses", [])) if user_info.get("current_courses") else "None",
        "interests": user_info.get("interests", "General interest in computer science"),
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