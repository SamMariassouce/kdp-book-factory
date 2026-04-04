import os
import pandas as pd
import google.generativeai as genai
import time

# --- 1. SETUP ---
# Replace with your actual key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

def run_factory():
    print("\n--- BLISSITY PUBLICATIONS: NICHE ARCHITECT v1.0 ---")
    
    # Drag and drop the CSV from the 01_Market_CSVs folder
    csv_path = input("Drag and drop the Rocket Keyword CSV here: ").strip().replace("'", "").replace('"', "").replace("\\ ", " ")
    
    if not os.path.exists(csv_path):
        print("Error: CSV not found. Make sure the path is correct.")
        return

    # Load data for the AI
    try:
        df = pd.read_csv(csv_path)
        market_snapshot = df.head(20).to_string() # Giving AI the top 20 keywords
        niche_label = os.path.basename(csv_path).split(" - ")[-1].replace(".csv", "").replace(" ", "_")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"\n[1/3] Brain is analyzing {niche_label} market data...")

    # --- 2. THE MASTER PROMPT (Blissity Logic) ---
    prompt = f"""
    You are the Lead Product Strategist at Blissity Publications. 
    Analyze this Publisher Rocket CSV data: 
    {market_snapshot}
    
    TASK: Execute a full 10-book niche rollout.
    
    1. MASTER STRATEGY: Identify the 'Goldilocks' keyword and a 30-day launch roadmap.
    2. BOOK CONCEPTS: Create 10 unique books. For each, specify:
       - Title & Subtitle (SEO Optimized).
       - Type (Type A: Static Interior | Type B: Dynamic with Quotes).
       - Trim Size & Page Count.
       - AIDA Marketing Description (150-200 words).
       - 7 Backend Search Keywords.
    3. SUMMARY CHECKLIST: A 'Cover-Template-Checklist' for all 10 books.
    4. PINTEREST: 5 unique Pin Headlines/Descriptions with AI Image Prompts for each book.
    5. WEBFLOW: A CSV-formatted line for each book for CMS import (Title, Slug, Meta-Description).

    Output this as a structured document using Markdown headers.
    """

    # --- 3. EXECUTION ---
    try:
        response = model.generate_content(prompt)
        content = response.text

        # Create Project Folder
        project_root = os.path.join("..", "02_Niche_Projects", niche_label)
        os.makedirs(project_root, exist_ok=True)

        # Save the Master Document
        master_file = os.path.join(project_root, f"00_{niche_label}_FULL_BLUEPRINT.md")
        with open(master_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[2/3] Blueprint generated. Building folder structures...")

        # Create the 10 Production Folders
        for i in range(1, 11):
            book_name = f"Book_{i}_Production"
            book_path = os.path.join(project_root, book_name)
            
            # Create sub-folders for the 1,000-book pipeline
            subfolders = [
                "01_KDP_Final_Files", 
                "02_Digital_Interactive_Edition", 
                "03_Marketing_Pins", 
                "04_Webflow_Assets",
                "05_Internal_Guides"
            ]
            for folder in subfolders:
                os.makedirs(os.path.join(book_path, folder), exist_ok=True)
            
            # Create the initial Assembly Guide
            guide_path = os.path.join(book_path, "05_Internal_Guides", "assembly-guide.txt")
            with open(guide_path, "w") as g:
                g.write(f"NICHE: {niche_label}\nBOOK_ID: {i}\nSTATUS: Awaiting Asset Generation\n")

        print(f"\n[3/3] SUCCESS!")
        print(f"Project Location: {os.path.abspath(project_root)}")
        print("-" * 40)
        
    except Exception as e:
        print(f"An error occurred during AI generation: {e}")

if __name__ == "__main__":
    run_factory()