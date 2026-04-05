import keyboard
import sys
from datetime import datetime
from capture import get_selected_text
from vault_manager import list_notes, append_to_note, create_note, log_to_history
from llm_client import unified_process
from notifier import show_toast

# You can change the hotkey to anything you prefer
HOTKEY = 'f9'

import time

LAST_TRIGGER_TIME = 0

def trigger_logging():
    global LAST_TRIGGER_TIME
    current_time = time.time()
    
    # Debounce: Prevent double-triggering within 2 seconds
    if current_time - LAST_TRIGGER_TIME < 2.0:
        return
    LAST_TRIGGER_TIME = current_time
    
    print("\n" + "="*50)
    print("Obsidian Intelligent Logger: Capturing...")
    
    # Visual Feedback Start
    show_toast("Analyzing & Routing Research...", title="Thinking", icon="🧠", duration=2.0)
    
    start_time = time.time()
    captured_text, window_title, url = get_selected_text()
    
    if not captured_text.strip():
        show_toast("No text selected!", title="Error", icon="❌")
        return

    # 1. Unified AI Processing (Combining Routing & Synthesis)
    notes = list_notes()
    topic, formatted_content = unified_process(captured_text, notes, window_title)
    
    # 2. Metadata Handling
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url_line = f" | [URL]({url})" if url else ""
    metadata_footer = f"\n\n---\n> **Source:** {window_title}{url_line} | **Captured on:** {timestamp}"
    formatted_content += metadata_footer
    
    # 3. Save to Vault
    is_new = topic not in notes
    if is_new:
        success = create_note(topic, formatted_content)
    else:
        success = append_to_note(topic, formatted_content)
        
    # 4. History Logging
    log_to_history(timestamp, topic, captured_text[:150], f"{window_title}{url_line}")
    
    elapsed = time.time() - start_time
    print(f"SUCCESS: Logged to '{topic}' in {elapsed:.1f}s")
    
    if success:
        show_toast(f"Saved to: {topic}\n(Took {elapsed:.1f}s)", title="Logged to Vault", icon="✅")
    else:
        show_toast("Could not save note to vault.", title="Error", icon="❌")

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
