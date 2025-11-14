#!/usr/bin/env python3
"""
Dashboard HTML Auto-Updater
Automatically adds new content cards to index.html
"""

import json
import re
from bs4 import BeautifulSoup

def update_dashboard():
    """
    Updates index.html with new content cards
    """
    
    print("🔄 Starting Dashboard Update...")
    print()
    
    # Load new content
    try:
        with open('new_content.json', 'r') as f:
            data = json.load(f)
            new_resources = data['resources']
    except FileNotFoundError:
        print("❌ new_content.json not found. Run generate_content.py first.")
        return False
    
    print(f"📥 Found {len(new_resources)} new resources to add")
    print()
    
    # Read current HTML
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("❌ index.html not found in current directory")
        return False
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the days grid
    days_grid = soup.find('div', class_='days-grid')
    if not days_grid:
        print("❌ Could not find .days-grid element in HTML")
        return False
    
    print("✅ Found days grid section")
    print()
    
    # Add new cards
    print("➕ Adding new day cards...")
    for resource in new_resources:
        card_html = create_card_html(resource)
        new_card = BeautifulSoup(card_html, 'html.parser')
        days_grid.append(new_card)
        print(f"   ✅ Added Day {resource['day']}: {resource['title']}")
    
    print()
    
    # Update passwords in JavaScript
    print("🔑 Updating passwords in JavaScript...")
    updated_js = update_passwords_js(str(soup), new_resources)
    soup = BeautifulSoup(updated_js, 'html.parser')
    print("   ✅ Passwords updated")
    print()
    
    # Update PDF file paths
    print("📄 Updating PDF file paths...")
    updated_js = update_pdf_paths_js(str(soup), new_resources)
    soup = BeautifulSoup(updated_js, 'html.parser')
    print("   ✅ PDF paths updated")
    print()
    
    # Write updated HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    
    print("✅ Dashboard updated successfully!")
    print()
    print("📊 Summary:")
    for r in new_resources:
        print(f"   Day {r['day']}: {r['title']} (Password: {r['password']})")
    print()
    
    return True

def create_card_html(resource):
    """Generate HTML for new day card"""
    
    # Generate key points HTML
    key_points_html = ""
    for point in resource.get('key_points', []):
        key_points_html += f"                <li>{point}</li>\n"
    
    # Determine gradient colors based on day number
    gradients = [
        "linear-gradient(135deg, #ff006e, #8338ec)",
        "linear-gradient(135deg, #8338ec, #00f2ea)",
        "linear-gradient(135deg, #00f2ea, #3a86ff)",
        "linear-gradient(135deg, #3a86ff, #ff006e)",
        "linear-gradient(135deg, #ff006e, #fb5607)",
        "linear-gradient(135deg, #fb5607, #ffbe0b)",
        "linear-gradient(135deg, #ffbe0b, #00f2ea)",
        "linear-gradient(135deg, #00f2ea, #8338ec)",
        "linear-gradient(135deg, #8338ec, #ff006e)",
        "linear-gradient(135deg, #ff006e, #3a86ff)"
    ]
    
    gradient = gradients[(resource['day'] - 1) % len(gradients)]
    
    # Generate placeholder image or use generic gradient
    # You can add logic here to use actual images if available
    image_src = f"day_{resource['day']}_placeholder.jpg"  # Placeholder for now
    
    card_html = f'''
                <!-- Day {resource['day']} -->
                <div class="day-card">
                    <div class="day-card-image" style="background: {gradient};">
                        <div class="day-number-overlay">Day {resource['day']}</div>
                    </div>
                    <div class="day-card-content">
                        <span class="day-badge">Day {resource['day']} • {resource['category']}</span>
                        <h3 class="day-title">{resource['title']}</h3>
                        <p class="day-description">{resource['hook']}</p>
                        <ul class="day-points">
{key_points_html}                        </ul>
                        <button class="download-btn locked-btn" onclick="showPasswordModal('day{resource['day']}', '{resource['title']}')">
                            🔒 Unlock Day {resource['day']} PDF
                        </button>
                    </div>
                </div>
'''
    
    return card_html

def update_passwords_js(html_content, resources):
    """Add new passwords to JavaScript passwords object"""
    
    # Find the passwords object
    password_pattern = r'const passwords = \{([^}]+)\};'
    match = re.search(password_pattern, html_content, re.DOTALL)
    
    if not match:
        print("   ⚠️  Warning: Could not find passwords object")
        return html_content
    
    current_passwords = match.group(1)
    
    # Add new passwords
    new_password_entries = []
    for resource in resources:
        day_key = f"day{resource['day']}"
        password = resource['password']
        new_password_entries.append(f"            {day_key}: '{password}'")
    
    # Combine with existing
    updated_passwords = current_passwords.rstrip().rstrip(',') + ',\n' + ',\n'.join(new_password_entries)
    
    # Replace in HTML
    updated_html = html_content.replace(
        f"const passwords = {{{current_passwords}}}",
        f"const passwords = {{\n{updated_passwords}\n        }}"
    )
    
    return updated_html

def update_pdf_paths_js(html_content, resources):
    """Add new PDF file paths to JavaScript pdfFiles object"""
    
    # Find the pdfFiles object
    pdf_pattern = r'const pdfFiles = \{([^}]+)\};'
    match = re.search(pdf_pattern, html_content, re.DOTALL)
    
    if not match:
        print("   ⚠️  Warning: Could not find pdfFiles object")
        return html_content
    
    current_pdfs = match.group(1)
    
    # Add new PDF paths
    new_pdf_entries = []
    for resource in resources:
        day_key = f"day{resource['day']}"
        # Generate filename from title
        pdf_filename = f"Day_{resource['day']}_{resource['title'].replace(' ', '_').replace('/', '_')}.pdf"
        new_pdf_entries.append(f"            {day_key}: '{pdf_filename}'")
    
    # Combine with existing
    updated_pdfs = current_pdfs.rstrip().rstrip(',') + ',\n' + ',\n'.join(new_pdf_entries)
    
    # Replace in HTML
    updated_html = html_content.replace(
        f"const pdfFiles = {{{current_pdfs}}}",
        f"const pdfFiles = {{\n{updated_pdfs}\n        }}"
    )
    
    return updated_html

def update_section_title(html_content, highest_day):
    """Update the section title to reflect new day range"""
    
    # Update "10-Day Career Acceleration Series" to reflect actual range
    updated_html = re.sub(
        r'(\d+)-Day Career Acceleration Series',
        f'{highest_day}-Day Career Acceleration Series',
        html_content
    )
    
    return updated_html

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 Dashboard Auto-Updater")
    print("=" * 60)
    print()
    
    success = update_dashboard()
    
    if success:
        print("=" * 60)
        print("✅ Update Complete!")
        print("=" * 60)
        print()
        print("🚀 Next Steps:")
        print("   1. Commit changes to GitHub")
        print("   2. GitHub Pages will auto-deploy")
        print("   3. Site will be live in 2-3 minutes")
    else:
        print("=" * 60)
        print("❌ Update Failed")
        print("=" * 60)
