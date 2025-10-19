import chromadb
import json
from tqdm import tqdm

client = chromadb.PersistentClient(path="./chroma_db")

# Check if already loaded
try:
    req_collection = client.get_collection("requirements")
    print(f"✓ Requirements already loaded ({req_collection.count()} entries)")
    
    # Ask if user wants to reload
    reload = input("Reload requirements? (y/n): ")
    if reload.lower() != 'y':
        exit()
    client.delete_collection("requirements")
    print("Deleted old requirements collection")
except:
    print("Creating new requirements collection...")

# Load the JSON
with open('vector db/course_data/cs_requirements.json', 'r') as f:
    data = json.load(f)

# Extract CS requirements (it's in an array with one object)
cs_data = data[0]["CS"]

req_collection = client.create_collection("requirements")

documents = []
metadatas = []
ids = []

print("Processing CS requirements...")

# 1. General Requirements
if 'general_requirements' in cs_data:
    for category, info in cs_data['general_requirements'].items():
        text_parts = [f"CS Major - General Requirement: {category.replace('_', ' ').title()}"]
        text_parts.append(f"Total Credits: {info['total_credits']}")
        
        # Add requirement details if they exist
        if info['requirements']:
            for req in info['requirements']:
                req_type = req['requirement_type']
                courses = req.get('classes', req.get('courses', []))
                
                if req_type == "AND":
                    text_parts.append(f"Must take ALL of: {', '.join(courses)}")
                elif req_type == "OR":
                    text_parts.append(f"Must take ONE of: {', '.join(courses)}")
                elif req_type == "ANY":
                    text_parts.append(f"Can take any from: {', '.join(courses[:10])}...")  # Truncate if too long
        
        # Add notes
        if info['notes']:
            text_parts.append(f"Notes: {info['notes']}")
        
        text = "\n".join(text_parts)
        
        documents.append(text)
        metadatas.append({
            "major": "CS",
            "category": "general",
            "subcategory": category,
            "credits": info['total_credits']
        })
        ids.append(f"CS_general_{category}")

# 2. Math and Science
if 'math_and_science' in cs_data:
    for subject, info in cs_data['math_and_science'].items():
        text_parts = [f"CS Major - {subject.title()} Requirement"]
        text_parts.append(f"Total Credits: {info['total_credits']}")
        
        if info['requirements']:
            for req in info['requirements']:
                req_type = req['requirement_type']
                courses = req.get('classes', req.get('courses', []))
                
                if req_type == "AND":
                    text_parts.append(f"Must take ALL of: {', '.join(courses)}")
                elif req_type == "OR":
                    text_parts.append(f"Must take ONE of: {', '.join(courses)}")
        
        if info.get('notes'):
            text_parts.append(f"Notes: {info['notes']}")
        
        text = "\n".join(text_parts)
        
        documents.append(text)
        metadatas.append({
            "major": "CS",
            "category": "math_science",
            "subcategory": subject,
            "credits": info['total_credits']
        })
        ids.append(f"CS_math_science_{subject}")

# 3. Computer Science Core
if 'computer_science' in cs_data:
    for area, info in cs_data['computer_science'].items():
        text_parts = [f"CS Major - {area.replace('_', ' ').title()}"]
        text_parts.append(f"Total Credits: {info['total_credits']}")
        
        if info['requirements']:
            for req in info['requirements']:
                req_type = req['requirement_type']
                courses = req.get('classes', req.get('courses', []))
                
                if req_type == "AND":
                    text_parts.append(f"Option {req['requirement_id'] + 1}: Must take ALL of: {', '.join(courses)}")
                elif req_type == "OR":
                    text_parts.append(f"Must take ONE of: {', '.join(courses)}")
        
        if info.get('notes'):
            text_parts.append(f"Notes: {info['notes']}")
        
        text = "\n".join(text_parts)
        
        documents.append(text)
        metadatas.append({
            "major": "CS",
            "category": "computer_science",
            "subcategory": area,
            "credits": info['total_credits']
        })
        ids.append(f"CS_cs_{area}")

# Add to ChromaDB
print(f"\nAdding {len(documents)} requirement entries to ChromaDB...")
req_collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"\n✓ Loaded {len(documents)} CS requirement entries")

# Test searches
print("\n" + "="*60)
print("TESTING SEARCHES:")
print("="*60)

test_queries = [
    "What math classes do I need?",
    "CS fundamentals requirements",
    "What are the writing requirements?",
    "science requirements for CS major"
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    results = req_collection.query(
        query_texts=[query],
        n_results=2
    )
    print(f"Found: {results['ids'][0]}")
    print(f"Text preview: {results['documents'][0][0][:200]}...")
    print("-" * 60)