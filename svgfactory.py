import os
import re

# --- KDP 72 DPI BLEED TABLE (Cowork Step 4) ---
# Format: "Trim Size": (Width_px, Height_px)
TRIM_TABLE = {
    "6 x 9": (441, 666),
    "8.5 x 11": (621, 810),
    "8 x 10": (585, 738),
    "5.5 x 8.5": (405, 630),
    "8.25 x 11": (603, 810),
    "7.5 x 9.25": (549, 684),
    "5 x 8": (369, 594)
}

def get_specs_from_blueprint(book_title):
    """Scrapes BLUEPRINT.md for the specific book's Trim and Page Count."""
    blueprint_path = os.path.join("02_Niche_Projects", "BLUEPRINT.md")
    if not os.path.exists(blueprint_path):
        return None
    
    with open(blueprint_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Regex to find the block for the specific book
    pattern = rf"## \*\*Book \d+: {re.escape(book_title)}\*\*(.*?)(?=## \*\*Book \d+:|$)"
    block = re.search(pattern, content, re.DOTALL)
    if not block: return None
    
    text = block.group(1)
    trim = re.search(r"Trim Size:\s*([\d.]+\s*x\s*[\d.]+)", text)
    pages = re.search(r"Page Count:\s*(\d+)", text)
    
    return {
        "trim": trim.group(1) if trim else "6 x 9",
        "pages": int(pages.group(1)) if pages else 120
    }

def generate_svg(path, book_title, section_name, font, specs):
    """Generates a KDP-compliant SVG master template."""
    trim_key = specs['trim']
    w, h = TRIM_TABLE.get(trim_key, (441, 666))
    
    # Gutter calculation (Cowork Step 4 Rule)
    pages = specs['pages']
    gutter = 27 if pages <= 150 else 36 if pages <= 300 else 45
    outside = 27
    top_bot = 54 # 0.75" safe top/bottom
    
    safe_w = w - (gutter + outside)
    
    svg_content = f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white" />
    
    <rect x="{gutter}" y="{top_bot}" width="{safe_w}" height="35" fill="black" />
    <text x="{gutter + 10}" y="{top_bot + 24}" font-family="{font}, sans-serif" font-size="14" fill="white" font-weight="bold">{section_name.upper()}</text>
    
    <rect x="{gutter}" y="{top_bot + 45}" width="{safe_w}" height="{h - (top_bot * 2) - 60}" fill="none" stroke="black" stroke-width="0.5" />
    
    <text x="{w/2}" y="{h - 30}" font-family="{font}, sans-serif" font-size="10" fill="#666" text-anchor="middle">- Page -</text>
</svg>'''
    
    clean_name = section_name.lower().replace(" ", "-")
    filename = f"{book_title.lower().replace(' ', '-')}-{clean_name}.svg"
    
    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        f.write(svg_content)
    return filename

def run_svg_factory():
    base_folder = "02_Niche_Projects"
    # Get only directory names
    projects = sorted([d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))])
    
    print("\n🎨 SVG FACTORY — KDP TEMPLATE GENERATOR")
    for i, p in enumerate(projects):
        print(f"{i+1}. {p}")
    
    choice_idx = int(input("\nEnter book number: ")) - 1
    selected_book = projects[choice_idx]
    book_path = os.path.join(base_folder, selected_book)
    
    # 1. Get Metadata
    specs = get_specs_from_blueprint(selected_book)
    if not specs:
        print("❌ Error: Could not find book specs in BLUEPRINT.md")
        return

    # 2. Get Page Types from the first .md file in the folder (Workbook)
    md_files = [f for f in os.listdir(book_path) if f.endswith(".md") and "MANUSCRIPT" not in f]
    if not md_files:
        print(f"❌ Error: No Workbook .md found in {selected_book}")
        return
        
    with open(os.path.join(book_path, md_files[0]), "r", encoding="utf-8") as f:
        content = f.read()
    
    sections = re.findall(r"### (.*?)\n", content)

    # 3. Step 3: Font Selection
    print(f"\nTarget: {selected_book}")
    print(f"Specs: {specs['trim']} | {specs['pages']} pages")
    font = input("Enter Font (e.g., Playfair Display, Roboto, Montserrat): ") or "Lato"

    # 4. Generate SVGs
    created_files = []
    for s in sections:
        fname = generate_svg(book_path, selected_book, s.strip(), font, specs)
        created_files.append(fname)
        print(f"✅ Generated Master SVG: {fname}")

    # 5. Step 6: Generate Assembly Guide
    guide_name = f"{selected_book.lower().replace(' ', '-')}-assembly-guide.txt"
    with open(os.path.join(book_path, guide_name), "w", encoding="utf-8") as f:
        f.write(f"ASSEMBLY GUIDE — {selected_book}\n")
        f.write("="*40 + "\n")
        f.write(f"Trim: {specs['trim']} | Pages: {specs['pages']} | Font: {font}\n\n")
        f.write("ORDER OF PAGES:\n")
        f.write("1. Title Page (Content from Guide)\n2. Copyright Page\n3. How-to-use Guide\n")
        for f_name in created_files:
            f.write(f"-> Template: {f_name}\n")
    
    print(f"✅ Generated Guide: {guide_name}")
    
    # Final Completion Notification
    os.system(f'say "Book {choice_idx + 1} templates are ready."')
    os.system(f'osascript -e \'display notification "SVG Templates and Assembly Guide created successfully." with title "KDP Factory — Done"\'')

if __name__ == "__main__":
    run_svg_factory()