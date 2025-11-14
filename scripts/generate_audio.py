#!/usr/bin/env python3
"""
ElevenLabs Audio Generator
Generates professional voiceover for each day using Arabella voice
Saves to local directory: /Users/gregmansell/Desktop/automation/11labs
"""

import os
import json
from elevenlabs.client import ElevenLabs
from elevenlabs import save

def generate_audio_files():
    """
    Generate audio files for all new content using ElevenLabs
    Voice ID: Z3R5wn05IrDiVCyEkUrK (Arabella)
    """
    
    # Configuration
    VOICE_ID = "Z3R5wn05IrDiVCyEkUrK"  # Arabella
    # Use relative path for GitHub Actions compatibility
    OUTPUT_DIR = os.path.join(os.getcwd(), "audio_files")
    
    # Get API key
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ Error: ELEVENLABS_API_KEY not found")
        return []
    
    client = ElevenLabs(api_key=api_key)
    
    print("🎙️ Starting ElevenLabs Audio Generation...")
    print(f"Voice: Arabella (ID: {VOICE_ID})")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load new content
    try:
        with open('new_content.json', 'r') as f:
            data = json.load(f)
            resources = data['resources']
    except FileNotFoundError:
        print("❌ new_content.json not found")
        return []
    
    generated_files = []
    
    for i, resource in enumerate(resources, 1):
        print(f"[{i}/{len(resources)}] Generating audio for Day {resource['day']}...")
        
        # Create filename from title (exact match to content topic)
        title_clean = resource['title'].replace(' ', '_').replace('/', '_').replace(':', '').replace('?', '')
        filename = f"{title_clean}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Create script for audio
        script = create_audio_script(resource)
        
        print(f"   Title: {resource['title']}")
        print(f"   Filename: {filename}")
        print(f"   Script length: {len(script)} characters")
        
        try:
            # Generate audio
            audio = client.generate(
                text=script,
                voice=VOICE_ID,
                model="eleven_multilingual_v2"
            )
            
            # Save audio file
            save(audio, filepath)
            
            print(f"   ✅ Saved: {filepath}")
            
            generated_files.append({
                'day': resource['day'],
                'title': resource['title'],
                'filename': filename,
                'filepath': filepath,
                'script': script
            })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            continue
        
        print()
    
    # Save audio metadata
    audio_metadata = {
        'generated_at': data.get('generated_at'),
        'voice_id': VOICE_ID,
        'voice_name': 'Arabella',
        'output_directory': OUTPUT_DIR,
        'files': generated_files
    }
    
    with open('audio_files.json', 'w') as f:
        json.dump(audio_metadata, f, indent=2)
    
    print("=" * 60)
    print(f"✅ Generated {len(generated_files)} audio files")
    print(f"📁 Saved to: {OUTPUT_DIR}")
    print("=" * 60)
    print()
    
    return generated_files

def create_audio_script(resource):
    """
    Create a natural-sounding script for TikTok voiceover
    Optimized for 30-60 second videos
    """
    
    # Start with hook (attention grabber)
    script = f"{resource['hook']}. "
    
    # Add brief explanation
    script += f"{resource['description']} "
    
    # Add key points naturally
    script += "Here's what you need to know: "
    
    for i, point in enumerate(resource.get('key_points', [])[:3], 1):
        script += f"{point}. "
    
    # Call to action
    script += f"Want the full framework? Link in bio. DM me 'DAY{resource['day']}' for the password. Let's level up together!"
    
    return script

def create_extended_audio_script(resource):
    """
    Create longer script for YouTube or podcast content (2-3 minutes)
    """
    
    script = f"Day {resource['day']}: {resource['title']}. "
    script += f"{resource['hook']} "
    script += f"{resource['description']} "
    script += "\n\n"
    
    # Add full content summary
    content = resource.get('full_content', '')
    # Take first 500 words
    words = content.split()[:500]
    script += ' '.join(words)
    
    script += "\n\nFor the complete guide with examples and templates, check the link in the description. "
    script += f"And if you want even more resources, follow @alyssaharperadvice on TikTok."
    
    return script

if __name__ == "__main__":
    print("=" * 60)
    print("🎙️ ElevenLabs Audio Generator - Alyssa Harper")
    print("=" * 60)
    print()
    
    files = generate_audio_files()
    
    if files:
        print("🎉 Audio generation complete!")
        print()
        print("📋 Generated files:")
        for f in files:
            print(f"   - {f['filename']}")
    else:
        print("❌ No audio files generated")
