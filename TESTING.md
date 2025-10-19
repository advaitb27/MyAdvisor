# Testing Your UW Academic Advisor App

## Prerequisites

Make sure you have the following installed:
- Python 3.11+ (with conda environment `thirteen`)
- Node.js and npm
- All backend dependencies installed in your conda environment

## Step 1: Start the Backend

Open a terminal and run:

```bash
cd /Users/advaitbhargav/Documents/VScode/backend

# Activate your conda environment
conda activate thirteen

# Run the FastAPI backend
python backend.py
```

The backend should start on **http://localhost:8000**

You should see output like:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test the backend:** Open http://localhost:8000 in your browser. You should see:
```json
{
  "status": "Academic Advisor API Running (Gemini)",
  "courses_loaded": <number>,
  "requirements_loaded": <number>
}
```

## Step 2: Start the Frontend

Open a **new terminal** (keep the backend running) and run:

```bash
cd /Users/advaitbhargav/Documents/VScode/frontend

# Install dependencies (first time only)
npm install

# Start the React development server
npm start
```

The frontend should open automatically in your browser at **http://localhost:3000**

## Step 3: Test the Application

1. **Home Page**: You should see the home page with a "Get Started" or similar button

2. **Navigate to Chat**: Click the button to go to `/chat`

3. **Test the Chat**:
   - You should see a welcome message: "Hey User, how's the quarter going?"
   - Type a question like: "What math classes do I need for CS?"
   - Click send (or press Enter)
   - You should see "Thinking . . ." while the AI processes
   - The AI should respond with information from your course database

4. **Example Questions to Test**:
   - "What are the CS major requirements?"
   - "Tell me about CSE 311"
   - "What classes should I take next quarter?"
   - "Do I need to take MATH 126?"
   - "What are my options for the math requirement?"

## Troubleshooting

### Backend Issues

**Error: "Collection not found"**
- Run the database creation scripts:
  ```bash
  cd backend
  python "vector db/create_course_db.py"
  python "vector db/create_requirements_db.py"
  ```

**Error: "GOOGLE_API_KEY not found"**
- Make sure `.env` file exists in the `backend/` directory with your API key

**Error: "ModuleNotFoundError"**
- Install missing dependencies:
  ```bash
  pip install fastapi uvicorn chromadb langchain-google-genai python-dotenv
  ```

### Frontend Issues

**Error: "npm: command not found"**
- Install Node.js from https://nodejs.org/

**Blank page or errors in browser console**
- Check that the backend is running on http://localhost:8000
- Open browser DevTools (F12) to see error messages
- Make sure CORS is configured correctly in the backend

**Connection errors in chat**
- Verify backend is running: http://localhost:8000
- Check browser console for error messages
- Ensure the API endpoint in `ChatPage.tsx` is `http://localhost:8000/chat`

## What to Look For

✅ **Backend is working** if:
- Server starts without errors
- http://localhost:8000 shows the status JSON
- Course and requirement counts are greater than 0

✅ **Frontend is working** if:
- Home page loads
- Can navigate to chat page
- Input field accepts text

✅ **Full integration is working** if:
- Chat messages send successfully
- "Thinking . . ." appears while processing
- AI responses appear after a few seconds
- Responses mention actual course codes and requirements from your database

## Monitoring Logs

**Backend logs** (in the terminal running backend.py):
- You should see POST requests to `/chat` when you send messages
- Any errors will appear here

**Frontend logs** (browser DevTools Console):
- Network tab shows requests to http://localhost:8000/chat
- Console shows any JavaScript errors

## Next Steps

Once everything is working:
1. Try different questions to test the RAG system
2. Check if the AI correctly uses the course and requirement data
3. Test edge cases (unknown courses, invalid questions, etc.)
