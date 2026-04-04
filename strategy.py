import os
import pandas as pd
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Initialize
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# UPDATED: Using the correct 2026 preview string
MODEL_ID = "gemini-3-flash-preview"

def find_analyzed_file(folder):
    """Finds the keyword search file regardless of the long date/name."""
    for f in os.listdir(folder):
        if "analyzed" in f.lower() and f.endswith('.csv'):
            return os.path.join(folder, f)
    return None

def run_strategy():
    input_folder = "01_Market_CSVs"
    output_folder = "02_Niche_Projects"
    os.makedirs(output_folder, exist_ok=True)

    # --- PHASE 1: KEYWORD SELECTION ---
    kw_path = find_analyzed_file(input_folder)
    if not kw_path:
        print(f"❌ Error: No 'analyzed' CSV found in {input_folder}")
        return

    print(f"🧐 Reading keyword data: {os.path.basename(kw_path)}...")
    df = pd.read_csv(kw_path)
    # Analysis of top 50 keywords
    kw_intel = df.head(50).to_string()

    selection_prompt = f"""
    Act as a Data Scientist for a High-End KDP Publishing House.
    Analyze these 50 keywords. Based on earnings vs competition, select the top 5 'Gold Mine' keywords.
    Provide a simple list with a 1-sentence reason for each.
    
    DATA:
    {kw_intel}
    """

    print("🤖 AI is filtering for winners...")
    
    # UPDATED: Fixed configuration for Gemini 3 'Thinking' mode
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=selection_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )
    
    selected_keywords = response.text
    print("\n" + "="*40)
    print("🌟 AI SELECTED WINNERS TO RESEARCH:")
    print("="*40)
    print(selected_keywords)
    print("="*40)

    # --- PHASE 2: PAUSE FOR COMPETITION DATA ---
    print("\n🛑 PIPELINE PAUSED.")
    print("ACTION: Go to Publisher Rocket and get the COMPETITION CSVs for these winners.")
    print(f"ACTION: Drop those CSVs into: '{input_folder}'")
    input("\n➡️  Press ENTER when the competition files are ready in the folder...")

    # --- PHASE 3: FINAL BLUEPRINT CREATION ---
    print("\n🧠 Integrating all data into the Master Blueprint...")
    
    all_comp_data = ""
    found_files = 0
    for f in os.listdir(input_folder):
        if f.endswith(".csv") and "analyzed" not in f.lower():
            try:
                comp_df = pd.read_csv(os.path.join(input_folder, f))
                all_comp_data += f"\n--- DATA FROM {f} ---\n" + comp_df.head(15).to_string()
                found_files += 1
            except Exception as e:
                print(f"⚠️ Could not read {f}: {e}")
                continue

    final_prompt = f"""
    Create a 10-book 'BLUEPRINT.md'. 
    Use the Keywords we selected AND the Competition Data provided.
    
    SELECTED KEYWORDS:
    {selected_keywords}

    NEW COMPETITION INTEL:
    {all_comp_data}

    For each book:
    - **Book X: Full SEO Title**
    - MARKET GAP: Why will this win?
    - SPECS: Page count, Trim size, and Price.
    """

    # Using high reasoning for the final business strategy
    final_res = client.models.generate_content(
        model=MODEL_ID,
        contents=final_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )

    with open(f"{output_folder}/BLUEPRINT.md", "w", encoding="utf-8") as f:
        f.write(final_res.text)
    
    print("\n✅ SUCCESS! Master BLUEPRINT.md created.")

if __name__ == "__main__":
    run_strategy()