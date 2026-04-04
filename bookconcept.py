import os
import re
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.0-flash" 

def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def run_concepts():
    strategy_path = "02_Niche_Projects/BLUEPRINT.md"
    base_folder = "02_Niche_Projects"

    with open(strategy_path, "r", encoding="utf-8") as f:
        content = f.read()

    titles = re.findall(r"\*\*Book \d+: (.*?)\*\*", content)
    if not titles:
        titles = re.findall(r"\*\*(.*?)\*\*", content)[:10]

    print(f"🚀 Starting Resilient Build for {len(titles)} books...")

    for i, title in enumerate(titles):
        safe_title = sanitize(title)
        book_dir = os.path.join(base_folder, safe_title)
        os.makedirs(book_dir, exist_ok=True)
        file_path = os.path.join(book_dir, f"{safe_title}.md")

        # Skip if already created (so you can restart the script safely)
        if os.path.exists(file_path):
            print(f"⏭️  Skipping {safe_title} (Already exists)")
            continue

        success = False
        retries = 0
        
        while not success and retries < 3:
            print(f"🏗️  [{i+1}/10] Designing: {safe_title} (Attempt {retries + 1})...")
            prompt = f"Create a detailed KDP Concept & Interior Spec doc for: {title}."

            try:
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                with open(file_path, "w") as f:
                    f.write(response.text)
                print(f"✅ Created: {safe_title}")
                success = True
                time.sleep(15) # Standard cool-down
            except Exception as e:
                retries += 1
                if "503" in str(e) or "429" in str(e):
                    print(f"⚠️ Server busy/limit hit. Cooling down for 30s...")
                    time.sleep(30)
                else:
                    print(f"❌ Permanent Error: {e}")
                    break

    print("\n✨ Factory Cycle Complete.")

if __name__ == "__main__":
    run_concepts()