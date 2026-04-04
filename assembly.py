import os
import re

def get_blueprint_data(book_title):
    """
    Scrapes the BLUEPRINT.md to find the exact Specs for the chosen book.
    """
    with open("02_Niche_Projects/BLUEPRINT.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the block for the specific book
    # This regex looks for the Book Title and stops before the next "## Book"
    pattern = rf"## \*\*Book \d+: {re.escape(book_title)}\*\*(.*?)(?=## \*\*Book \d+:|$)"
    block = re.search(pattern, content, re.DOTALL)
    
    if not block:
        return None
    
    text = block.group(1)
    
    # Extract Trim (e.g., 6 x 9)
    trim_match = re.search(r"Trim Size:\s*([\d.]+\s*x\s*[\d.]+)", text)
    trim_str = trim_match.group(1) if trim_match else "6 x 9"
    
    # Extract Page Count
    page_match = re.search(r"Page Count:\s*(\d+)", text)
    pages = int(page_match.group(1)) if page_match else 120
    
    return {"trim": trim_str, "pages": pages}

def calculate_kdp_dims(trim_str, pages):
    """Applies KDP Full Bleed math (+0.125w, +0.25h) and Gutter rules."""
    # Pixel conversion (72 DPI)
    dims = {
        "6 x 9": (441, 666),
        "8.5 x 11": (621, 810),
        "8 x 10": (585, 738),
        "5.5 x 8.5": (405, 630),
        "8.25 x 11": (603, 810),
        "7.5 x 9.25": (549, 684),
        "5 x 8": (369, 594)
    }
    
    w, h = dims.get(trim_str, (441, 666)) # Default to 6x9
    
    # Gutter Logic based on Page Count
    if pages <= 150: gutter = 27
    elif pages <= 300: gutter = 36
    else: gutter = 45
    
    return w, h, gutter

def run_assembly():
    base = "02_Niche_Projects"
    folders = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])
    
    print("\n🚀 KDP BLUEPRINT ASSEMBLER")
    for i, f in enumerate(folders): print(f"{i+1}. {f}")
    
    choice = int(input("\nSelect book: ")) - 1
    selected_book = folders[choice]
    book_path = os.path.join(base, selected_book)
    
    # 1. Get Specs from Blueprint
    specs = get_blueprint_data(selected_book)
    if not specs:
        print("❌ Could not find specs in BLUEPRINT.md")
        return
        
    w, h, gutter = calculate_kdp_dims(specs['trim'], specs['pages'])
    print(f"📊 Mode: {specs['trim']} | Pages: {specs['pages']} | Gutter: {gutter}px")

    # 2. Find Page Types in Workbook.md
    md_file = [f for f in os.listdir(book_path) if f.endswith(".md") and "MANUSCRIPT" not in f][0]
    with open(os.path.join(book_path, md_file), "r") as f:
        content = f.read()
    
    page_types = re.findall(r"### (.*?)\n", content)
    
    # 3. Create SVGs
    for p in page_types:
        p_name = p.strip()
        safe_w = w - (gutter + 27)
        
        svg = f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white" />
            <rect x="{gutter}" y="54" width="{safe_w}" height="35" fill="black" />
            <text x="{gutter + 10}" y="78" font-family="sans-serif" font-size="14" fill="white">{p_name.upper()}</text>
            <rect x="{gutter}" y="100" width="{safe_w}" height="{h-180}" fill="none" stroke="black" stroke-width="0.5" />
        </svg>'''
        
        filename = f"{selected_book.lower().replace(' ', '-')}-{p_name.lower().replace(' ', '-')}.svg"
        with open(os.path.join(book_path, filename), "w") as f:
            f.write(svg)
        print(f"✅ Generated: {filename}")

    os.system(f'say "Assembly for {selected_book} complete."')

if __name__ == "__main__":
    run_assembly()