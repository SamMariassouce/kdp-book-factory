import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup & Keys
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def sanitize_name(name):
    """Removes characters that computers hate in folder names (like : / ?)"""
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    return clean.strip()

def run_concepts():
    # This looks for the file created by strategy.py
    strategy_path = "02_Niche_Projects/BLUEPRINT.md"
    base_folder = "02_Niche_Projects"

    if not os.path.exists(strategy_path):
        print(f"❌ Error: {strategy_path} not found. Run 'python strategy.py' first!")
        return

    # 2. Read the Master Strategy
    with open(strategy_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. Find the 10 Book Titles (looks for **Book X: Title**)
    titles = re.findall(r"\*\*Book \d+: (.*?)\*\*", content)
    
    if not titles:
        # Backup: if the AI used a different bolding style
        titles = re.findall(r"\*\*(.*?)\*\*", content)[:10]

    if not titles:
        print("❌ Could not find any book titles in BLUEPRINT.md. Check the file format!")
        return

    print(f"🚀 Found {len(titles)} books. Building your concept folders...")

    # 4. Connect to the 2026 Free Model
    model = genai.GenerativeModel('gemini-2.5-flash')

    for title in titles:
        # Create a clean name for the folder and the file
        safe_title = sanitize_name(title)
        book_dir = os.path.join(base_folder, safe_title)
        
        # Create the folder
        os.makedirs(book_dir, exist_ok=True)
        
        print(f"🏗️  Designing Concept: {safe_title}...")

        # The "Quality" Prompt
        prompt = f"""
        Act as a Premium KDP Product Designer. 
        Create a 'High-Quality Concept Document' for the book: "{title}"
        
        Provide:
        1. THE UNIQUE HOOK: Why is this better than competitors?
        2. TARGET AUDIENCE: Who is the buyer?
        3. INTERIOR BLUEPRINT: Exactly what goes on the pages?
        4. CHAPTER BREAKDOWN: Detailed Table of Contents.
        5. AI WRITING PROMPT: A master-instruction to write this book later.
        """

        try:
            response = model.generate_content(prompt)
            
            # Save the file INSIDE the folder, named after the book
            file_path = os.path.join(book_dir, f"{safe_title}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            print(f"✅ Success: Created folder and file for '{safe_title}'")
        except Exception as e:
            print(f"⚠️ Error on {title}: {e}")

    print(f"\n✨ DONE! Check your '{base_folder}' folder for your new book designs.")