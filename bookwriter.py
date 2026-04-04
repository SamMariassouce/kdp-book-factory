import os
import time
from google import genai
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
# The 2026 SDK automatically handles the 'models/' prefix
# Just provide the raw model name
MODEL_ID = "gemini-2.0-flash" 

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_writer():
    base_folder = "02_Niche_Projects"
    
    # Get sorted list of projects
    projects = sorted([d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))])
    
    print("\n🖋️  KDP CONTENT WRITER (2026 SDK EDITION)")
    for i, p in enumerate(projects):
        print(f"{i+1}. {p}")
    
    try:
        user_choice = input("\nEnter book number: ")
        if not user_choice: return
        choice = int(user_choice) - 1
        selected_book = projects[choice]
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return

    book_path = os.path.join(base_folder, selected_book)
    
    # Find the Concept file
    try:
        concept_file = [f for f in os.listdir(book_path) if f.endswith(".md") and "MANUSCRIPT" not in f][0]
    except IndexError:
        print(f"❌ No concept file found in {selected_book}")
        return

    with open(os.path.join(book_path, concept_file), "r", encoding="utf-8") as f:
        concept_text = f.read()

    sections = ["Introduction", "User Guide", "Glossary"]

    for section in sections:
        filename = f"MANUSCRIPT_{section.lower().replace(' ', '_')}.md"
        full_path = os.path.join(book_path, filename)

        if os.path.exists(full_path):
            print(f"⏭️  Skipping {filename}")
            continue

        print(f"✍️  Drafting {section}...")
        
        try:
            # CORRECT 2026 CALL FORMAT
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"Write a professional KDP {section} for the book '{selected_book}' using this concept: {concept_text}. Recommend Google Fonts."
            )
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ Saved: {filename}")
            
            # Brief pause for the Free Tier
            time.sleep(10)
            
        except Exception as e:
            # If 2.0 fails, it might be the Daily Quota. 
            # In that case, we change the MODEL_ID manually to 'gemini-1.5-flash'
            print(f"❌ Error on {section}: {e}")

if __name__ == "__main__":
    run_writer()