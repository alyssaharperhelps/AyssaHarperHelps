#!/usr/bin/env python3
"""
AI Content Generator for Alyssa Harper Career Resources
Uses Claude API to analyze trends and generate new content
"""

import os
import json
import re
from datetime import datetime
from anthropic import Anthropic
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor

def generate_new_content():
    """
    Uses Claude to analyze trending content and generate new scripts
    """
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found")
        return []
    
    client = Anthropic(api_key=api_key)
    
    print("🤖 Starting AI Content Generation...")
    print()
    
    # Load trending videos
    try:
        with open('trending_content.json', 'r') as f:
            trending_data = json.load(f)
            trending = trending_data['top_videos']
    except FileNotFoundError:
        print("❌ trending_content.json not found. Run scrape_tiktok.py first.")
        return []
    
    print(f"📊 Analyzing {len(trending)} trending videos...")
    print()
    
    # Extract viral elements
    viral_content = []
    for video in trending[:15]:
        viral_content.append({
            'text': video['text'][:500],
            'engagement': video['engagement_score'],
            'hashtags': video['hashtags'][:5]
        })
    
    # Determine next day number
    next_day = get_next_day_number()
    
    print(f"📝 Generating content for Days {next_day}-{next_day+2}...")
    print()
    
    # Create prompt for Claude
    prompt = f"""You are Alyssa Harper, a career and negotiation expert who helps professionals level up through practical, data-driven advice.

CONTEXT: You already have resources for Days 1-{next_day-1}. You need to create 3 NEW unique resources.

TRENDING TIKTOK CONTENT (for inspiration):
{json.dumps(viral_content, indent=2)}

TASK: Generate 3 brand new career resources in EXACTLY this format:

---
DAY: {next_day}
CATEGORY: [One word: Negotiation/LinkedIn/Interview/Career/Communication/etc]
TITLE: [Catchy 3-5 word title]
HOOK: [7-15 word attention-grabbing hook that makes people want to learn more]
DESCRIPTION: [One sentence value proposition]
KEY_POINT_1: [Specific, actionable bullet point]
KEY_POINT_2: [Specific, actionable bullet point]
KEY_POINT_3: [Specific, actionable bullet point]
PASSWORD: [ONE WORD in ALLCAPS, relevant to topic]
FULL_CONTENT:
[Write a 400-600 word detailed guide in this structure:
- Start with the problem/pain point
- Introduce the framework/method
- Break down 3-5 specific steps with examples
- Include real numbers/stats where possible
- End with call to action to implement
- Write in Alyssa Harper's confident, direct, no-BS voice]
---

[Repeat for Day {next_day+1} and Day {next_day+2}]

REQUIREMENTS:
- Each resource must be UNIQUE (different from Days 1-{next_day-1} and from each other)
- Focus on trending topics from the TikTok data
- Include specific numbers, frameworks, and examples
- Make it immediately actionable
- Use Alyssa Harper's voice: confident, direct, empowering
- Each password should be ONE WORD related to the topic

Generate 3 complete resources now:"""

    print("🧠 Asking Claude to generate content...")
    print()
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = message.content[0].text
        print("✅ Received response from Claude")
        print()
        
    except Exception as e:
        print(f"❌ Error calling Claude API: {str(e)}")
        return []
    
    # Parse response
    print("📖 Parsing generated content...")
    resources = parse_claude_response(content, next_day)
    
    print(f"✅ Parsed {len(resources)} resources")
    print()
    
    # Generate PDFs
    print("📄 Creating PDFs...")
    for resource in resources:
        create_professional_pdf(resource)
        print(f"   ✅ Created Day_{resource['day']}_PDF")
    
    print()
    
    # Save metadata
    output = {
        'generated_at': datetime.now().isoformat(),
        'resources': resources
    }
    
    with open('new_content.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("✅ Saved content metadata to new_content.json")
    print()
    print("🎉 Content Generation Complete!")
    print()
    print("📋 Summary:")
    for r in resources:
        print(f"   Day {r['day']}: {r['title']}")
    print()
    
    return resources

def get_next_day_number():
    """Determine the next day number by checking existing content"""
    # Check index.html for highest day number
    try:
        with open('index.html', 'r') as f:
            content = f.read()
            # Find all "Day X" patterns
            days = re.findall(r'Day (\d+)', content)
            if days:
                return max([int(d) for d in days]) + 1
    except:
        pass
    
    # Default to day 11 if can't determine
    return 11

def parse_claude_response(content, start_day):
    """Parse Claude's response into structured data"""
    resources = []
    
    # Split by ---
    sections = content.split('---')
    
    day_counter = start_day
    
    for section in sections:
        if not section.strip():
            continue
            
        resource = {}
        
        # Extract fields using regex
        day_match = re.search(r'DAY:\s*(\d+)', section, re.IGNORECASE)
        if day_match:
            resource['day'] = int(day_match.group(1))
        else:
            resource['day'] = day_counter
            day_counter += 1
        
        category_match = re.search(r'CATEGORY:\s*(.+)', section, re.IGNORECASE)
        resource['category'] = category_match.group(1).strip() if category_match else "Career"
        
        title_match = re.search(r'TITLE:\s*(.+)', section, re.IGNORECASE)
        resource['title'] = title_match.group(1).strip() if title_match else "Untitled"
        
        hook_match = re.search(r'HOOK:\s*(.+)', section, re.IGNORECASE)
        resource['hook'] = hook_match.group(1).strip() if hook_match else ""
        
        desc_match = re.search(r'DESCRIPTION:\s*(.+)', section, re.IGNORECASE)
        resource['description'] = desc_match.group(1).strip() if desc_match else ""
        
        # Extract key points
        key_points = []
        for i in range(1, 4):
            point_match = re.search(f'KEY_POINT_{i}:\s*(.+)', section, re.IGNORECASE)
            if point_match:
                key_points.append(point_match.group(1).strip())
        resource['key_points'] = key_points
        
        password_match = re.search(r'PASSWORD:\s*(\w+)', section, re.IGNORECASE)
        resource['password'] = password_match.group(1).upper() if password_match else "ACCESS"
        
        # Extract full content
        content_match = re.search(r'FULL_CONTENT:\s*(.+)', section, re.IGNORECASE | re.DOTALL)
        if content_match:
            full_content = content_match.group(1).strip()
            # Remove any trailing --- or next section markers
            full_content = full_content.split('---')[0].strip()
            resource['full_content'] = full_content
        else:
            resource['full_content'] = "Content not found."
        
        # Only add if we have minimum required fields
        if resource.get('title') and resource.get('full_content'):
            resources.append(resource)
    
    return resources

def create_professional_pdf(resource):
    """Create a professional PDF from resource data"""
    
    filename = f"Day_{resource['day']}_{resource['title'].replace(' ', '_').replace('/', '_')}.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#ff006e'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#00f2ea'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#ff006e'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=10,
        fontName='Helvetica'
    )
    
    # Build document
    story = []
    
    # Header
    story.append(Paragraph("Alyssa Harper Helps", subtitle_style))
    story.append(Paragraph(resource['title'], title_style))
    story.append(Paragraph(f"Day {resource['day']} • {resource['category']}", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Hook
    if resource.get('hook'):
        story.append(Paragraph(f"<b>{resource['hook']}</b>", heading_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Key Points
    if resource.get('key_points'):
        story.append(Paragraph("Key Takeaways:", heading_style))
        for point in resource['key_points']:
            story.append(Paragraph(f"→ {point}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Full Content
    # Split into paragraphs
    paragraphs = resource['full_content'].split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_text = f"© 2025 Alyssa Harper Helps | Follow @alyssaharperadvice on TikTok"
    story.append(Paragraph(footer_text, subtitle_style))
    
    # Build PDF
    doc.build(story)
    
    return filename

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Content Generator - Alyssa Harper")
    print("=" * 60)
    print()
    
    resources = generate_new_content()
    
    if resources:
        print("=" * 60)
        print("✅ Generation Complete!")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Generation Failed")
        print("=" * 60)
