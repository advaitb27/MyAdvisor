import chromadb
import json
from tqdm import tqdm
import os

# Get the script directory to make paths work from anywhere
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)

client = chromadb.PersistentClient(path=os.path.join(backend_dir, "chroma_db"))

# Check if already loaded
try:
    existing_collection = client.get_collection("requirements")
    print(f"✓ Requirements already loaded ({existing_collection.count()} entries)")

    # Ask if user wants to reload
    reload = input("Reload requirements? (y/n): ")
    if reload.lower() != 'y':
        exit()
    client.delete_collection("requirements")
    print("Deleted old requirements collection")
except:
    pass

print("Creating new requirements collection...")

# Load the JSON
json_path = os.path.join(script_dir, 'course_data', 'cs_requirements.json')
with open(json_path, 'r') as f:
    data = json.load(f)

# Extract CS requirements (it's in an array with one object)
cs_data = data[0]["CS"]

req_collection = client.create_collection("requirements")

documents = []
metadatas = []
ids = []

print("Processing CS requirements...")

def process_requirement_section(section_data, category_name, display_prefix):
    """
    Generalized function to process any requirement section.
    Automatically handles single requirements vs multiple options.
    """
    for subcategory, info in section_data.items():
        text_parts = [f"CS Major - {display_prefix}: {subcategory.replace('_', ' ').title()}"]
        text_parts.append(f"Total Credits: {info['total_credits']}")

        if info['requirements']:
            # Check if there are multiple requirement_ids (mutually exclusive options)
            req_ids = set(req['requirement_id'] for req in info['requirements'])

            if len(req_ids) > 1:
                # Multiple options - student chooses ONE
                text_parts.append("Choose ONE of the following options:")
                for req in info['requirements']:
                    req_type = req['requirement_type']
                    courses = req.get('classes', req.get('courses', []))
                    option_num = req['requirement_id'] + 1

                    if req_type == "AND":
                        text_parts.append(f"  Option {option_num}: Take ALL of {', '.join(courses)}")
                    elif req_type == "OR":
                        text_parts.append(f"  Option {option_num}: Take ONE of {', '.join(courses)}")
                    elif req_type == "ANY":
                        text_parts.append(f"  Option {option_num}: Take any from {', '.join(courses[:10])}...")
            else:
                # Single requirement path (or same requirement_id for all)
                for req in info['requirements']:
                    req_type = req['requirement_type']
                    courses = req.get('classes', req.get('courses', []))

                    if req_type == "AND":
                        text_parts.append(f"Must take ALL of: {', '.join(courses)}")
                    elif req_type == "OR":
                        text_parts.append(f"Must take ONE of: {', '.join(courses)}")
                    elif req_type == "ANY":
                        text_parts.append(f"Can take any from: {', '.join(courses[:10])}...")

        # Add notes
        if info.get('notes'):
            text_parts.append(f"Notes: {info['notes']}")

        text = "\n".join(text_parts)

        documents.append(text)
        metadatas.append({
            "major": "CS",
            "category": category_name,
            "subcategory": subcategory,
            "credits": info['total_credits']
        })
        ids.append(f"CS_{category_name}_{subcategory}")

# 1. General Requirements
if 'general_requirements' in cs_data:
    process_requirement_section(
        cs_data['general_requirements'],
        "general",
        "General Requirement"
    )

# 2. Math and Science
if 'math_and_science' in cs_data:
    process_requirement_section(
        cs_data['math_and_science'],
        "math_science",
        "Math/Science Requirement"
    )

# 3. Computer Science Core
if 'computer_science' in cs_data:
    process_requirement_section(
        cs_data['computer_science'],
        "computer_science",
        "Computer Science Requirement"
    )

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