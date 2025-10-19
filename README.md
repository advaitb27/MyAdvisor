# UW Academic Advisor - AI-Powered Course Planning Assistant

An intelligent academic advising chatbot built with RAG (Retrieval-Augmented Generation) to help University of Washington students navigate course requirements, prerequisites, and academic planning.

## About the Project

As UW students, we often found ourselves overwhelmed by the complexity of degree requirements, course prerequisites, and scheduling. The official tools, while helpful, lacked the conversational, personalized guidance that would make academic planning less stressful, and advisors can only handle hundreds of students everyday. We wanted to build an AI-powered advisor that could supplement students' academic careers by answering questions like "What classes should I take next quarter?" or "Do I meet the prerequisites for CSE 373?" in a natural, intuitive way.

## What We Learned

This project was our deep dive into **Retrieval-Augmented Generation (RAG)** and modern LLM applications:

- **Vector Databases**: We implemented ChromaDB to store and efficiently search through thousands of course descriptions and degree requirements using semantic similarity
- **LLM Integration**: We integrated Google's Gemini model to generate contextual, helpful responses based on retrieved information
- **Full-Stack Development**: We built a complete application with FastAPI backend and React frontend, handling real-time chat interactions
- **Data Engineering**: We parsed and structured course catalog data from multiple sources (CSV, JSON) into a queryable format

## How We Built It

### Backend (Python + FastAPI)
- Created a RAG pipeline using ChromaDB for vector storage and semantic search
- Integrated Google's Gemini LLM (gemini-2.5-flash) through LangChain for natural language responses
- Built RESTful API endpoints for chat, profile management, and course search
- Implemented context-aware prompting that considers the user's major, completed courses, and current quarter

### Frontend (React + TypeScript)
- Designed an intuitive chat interface for students to ask questions
- Created components for user profiles, FAQs, and course search
- Implemented real-time communication with the backend API
- Built a responsive UI with modern design using Lucide icons and custom animations

### Data Pipeline
- Scraped and parsed UW course catalog data across multiple quarters
- Structured degree requirement documents for efficient retrieval
- Generated embeddings for semantic search using ChromaDB's built-in models

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **ChromaDB** - Vector database for semantic search
- **LangChain** - Framework for LLM application development
- **Google Gemini** (gemini-2.5-flash) - Large language model
- **Python-dotenv** - Environment variable management

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type-safe JavaScript
- **React Router** - Client-side routing
- **React Markdown** - Rendering formatted responses
- **Lucide React** - Icon library
- **Motion** - Animation library

## Challenges We Faced

1. **Data Quality**: Course catalog data was inconsistent across quarters and campuses. We had to write robust parsers to handle various formats and edge cases.

2. **Context Window Management**: Balancing the amount of context sent to the LLM was tricky. Too much information led to slow responses; too little resulted in inaccurate answers. We settled on retrieving the top 5 courses and 3 requirement documents.

3. **Semantic Search Tuning**: Getting relevant results from vector search required experimentation with chunk sizes and metadata filtering. Some queries about specific course codes needed exact matching, while others benefited from semantic similarity.

4. **Dependency Hell**: BeautifulSoup's lxml parser requirement caused deployment headaches—a reminder to always document dependencies clearly!

## Project Structure

```
├── backend/
│   ├── backend.py              # FastAPI application with RAG implementation
│   ├── chroma_db/              # Persistent vector database
│   └── vector db/              # Database creation scripts
│       ├── create_course_db.py
│       └── create_requirements_db.py
├── frontend/
│   └── src/
│       ├── Components/
│       │   ├── ChatPage.tsx    # Main chat interface
│       │   ├── Home.tsx        # Landing page
│       │   ├── FAQ.tsx         # Frequently asked questions
│       │   ├── ChatBar.tsx     # Chat input component
│       │   └── ShinyText.tsx   # Animated text component
│       ├── App.tsx             # Main application component
│       └── index.tsx           # Application entry point
├── catalog.json                # UW course catalog data (8MB)
├── .env.example                # Environment variable template
├── README.md                   # This file
└── TESTING.md                  # Setup and testing guide
```