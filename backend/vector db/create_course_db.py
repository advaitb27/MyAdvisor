import chromadb
import json
from datetime import datetime
from tqdm import tqdm

# Save to disk instead of memory
client = chromadb.PersistentClient(path="./chroma_db")

with open('vector db/course_data/catalog.json', 'r') as f:
    courses = json.load(f)

# Check if collection already exists
try:
    courses_collection = client.get_collection(name="courses")
    print(f"✓ Loaded existing collection with {courses_collection.count()} courses")
    print("Skipping data load (already exists)")
    
except:
    # Collection doesn't exist, create and load it
    print("Collection not found. Creating new collection...")
    courses_collection = client.create_collection(name="courses")
    
    documents = []
    metadatas = []
    ids = []
    index = 1
    id_set = set()
    skipped_none = 0
    skipped_duplicate = 0
    
    # Process courses with progress bar
    for course in tqdm(courses, desc="Processing courses"):
        if course['course_id'] in id_set:
            skipped_duplicate += 1
            continue
        
        if (course['course_id'] is None or
            course['course_name'] is None or
            course['quarter'] is None or
            course['credits'] is None):
            skipped_none += 1
            continue
        
        schedule_text = ""
        for i, section in enumerate(course['sections'], 1):
            if section.get('sln') is None:
                continue
            schedule_text += f"Section {i}: {section['days']} {section['time']}. "
            schedule_text += f"SLN: {section['sln']} "
        
        text = f"""
        {course['course_id']}
        {course['course_name']}
        Prerequisites: {course['prerequisites']}
        Quarter: {course['quarter']}
        Credits: {course['credits']}
        {schedule_text}
        """
        
        documents.append(text)
        metadatas.append({
            "course_id": course['course_id'],
            "credits": course['credits']
        })
        ids.append(course['course_id'])
        id_set.add(course['course_id'])
        index += 1
    
    print(f"\n✓ Processed {len(ids)} unique courses")
    print(f"  - Skipped {skipped_duplicate} duplicates")
    print(f"  - Skipped {skipped_none} courses with None values")
    
    # Add to ChromaDB in batches
    BATCH_SIZE = 2500
    total_added = 0
    
    print(f"\nAdding {len(documents)} courses to ChromaDB in batches of {BATCH_SIZE}...")
    now = datetime.now()
    
    for i in tqdm(range(0, len(documents), BATCH_SIZE), desc="Adding to ChromaDB"):
        batch_end = min(i + BATCH_SIZE, len(documents))
        
        courses_collection.add(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end]
        )
        total_added += (batch_end - i)
    
    then = datetime.now()
    print(f"\n✓ Added {total_added} courses to ChromaDB")
    print(f"  Took {then - now} to add to ChromaDB.")

# Test search (works whether newly created or loaded from disk)
results = courses_collection.query(
    query_texts=["AI class"],
    n_results=4
)

print(results['ids'])