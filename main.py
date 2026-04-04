import keyboard
import sys
from datetime import datetime
from capture import get_selected_text
from vault_manager import list_notes, append_to_note, create_note, log_to_history
from llm_client import decide_note_routing, generate_note_content, generate_new_topic_name
from notifier import show_toast

# You can change the hotkey to anything you prefer
HOTKEY = 'f9'

def trigger_logging():
    print("\n--- Capture triggered! Processing... ---")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text, window_title, url = get_selected_text()
    
    if not text.strip():
        print("Error: No text captured/selected! Please highlight some text first.")
        print("-" * 40)
        return
        
    source_display = window_title
    if url:
        source_display = f"[{window_title}]({url})"
        print(f"Captured snippet from browser: {url} ({len(text)} chars).")
    else:
        print(f"Captured snippet from '{window_title}' ({len(text)} chars). Querying Gemma 2 for routing...")
    
    notes = list_notes()
    
    # 1. Routing
    decision = decide_note_routing(text, notes)
    print(f"Gemma 2 Routing Decision: '{decision}'")
    
    # Safety clean-up in case Gemma outputs hallucinated tags
    topic_name = "NEW"
    for note in notes:
        # Case insensitive check if the exact note title was in the output
        if note.lower() in decision.lower():
            topic_name = note
            break
            
    is_new = False
    if topic_name == "NEW" or "NEW" in decision:
        print("Gemma 2 detected a new topic. Generating title...")
        topic_name = generate_new_topic_name(text)
        is_new = True
        
    # 2. Generation & Formatting
    print(f"Formatting markdown for topic: '{topic_name}'...")
    llm_response = generate_note_content(text, topic_name, notes, window_title, timestamp)
    
    # SAFETY FALLBACK: If LLM fails to return content, use the raw text
    if not llm_response.strip() or len(llm_response.strip()) < 5:
        print("Warning: LLM returned empty or too short response. Using raw text fallback.")
        formatted_content = text
    else:
        formatted_content = llm_response
    
    # Append Metadata reliably in Python
    url_line = f" | **URL:** {url}" if url else ""
    metadata_footer = f"\n\n-- ---\n> **Source:** {window_title}{url_line} | **Captured on:** {timestamp}"
    formatted_content += metadata_footer
    
    # 3. Save to Vault
    if is_new:
        result = create_note(topic_name, formatted_content)
    else:
        result = append_to_note(topic_name, formatted_content)
        
    # 4. History Logging
    log_to_history(timestamp, topic_name, text[:150], window_title, url)
    
    print(f"SUCCESS: {result}")
    show_toast(f"[[{topic_name}]]")
    print("-" * 40)

def main():
    print("="*50)
    print("Obsidian Intelligent Logger via Gemma 2 🧠")
    print(f"Trigger: [{HOTKEY}] | Reloading enabled via launcher.py")
    print("="*50)
    
    keyboard.add_hotkey(HOTKEY, trigger_logging)
    keyboard.wait()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Obsidian Logger...")
        sys.exit(0)
