import os
import glob

VAULT_PATH = r"C:\Users\vaibh\OneDrive\Documents\Obsidian Vault\Zettelkasten (Notes)"

def list_notes():
    """Returns a list of all markdown filenames in the vault, without extension."""
    if not os.path.exists(VAULT_PATH):
        print(f"WARNING: Vault path not found at {VAULT_PATH}")
        return []
    
    notes = []
    # Search for all markdown files recursively
    for filepath in glob.glob(os.path.join(VAULT_PATH, "**", "*.md"), recursive=True):
        basename = os.path.basename(filepath)
        name, _ = os.path.splitext(basename)
        notes.append(name)
    return notes

def append_to_note(topic_name, content):
    """Appends content to an existing note."""
    # Find the exact path of the topic
    for filepath in glob.glob(os.path.join(VAULT_PATH, "**", "*.md"), recursive=True):
        basename = os.path.basename(filepath)
        name, _ = os.path.splitext(basename)
        if name.lower() == topic_name.lower():
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n\n---\n\n{content}\n")
            return f"Appended to existing note: {name}"
    
    # Fallback if not found but LLM decided it
    return create_note(topic_name, content)

def create_note(topic_name, content):
    """Creates a new note in the root of the vault."""
    # Ensure invalid filesystem characters are removed from the topic
    safe_topic = "".join(c for c in topic_name if c.isalnum() or c in (' ', '-', '_')).strip()
    
    filepath = os.path.join(VAULT_PATH, f"{safe_topic}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {topic_name}\n\n{content}\n")
    return f"Created new note: {safe_topic}"

def log_to_history(timestamp, topic, summary, source_window, url=None):
    """Maintains a chronological log of all captures in _Logger History.md."""
    history_file = os.path.join(VAULT_PATH, "_Logger History.md")
    
    # Create file with header if it doesn't exist OR if the header is missing
    header_found = False
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "| --- | --- |" in content:
                header_found = True
    
    if not header_found:
        header = "# 📜 Logger History\n\n| Timestamp | Topic | Summary | Source |\n| --- | --- | --- | --- |\n"
        # Overwrite/Create with header
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    # Clean up summary (absolute single-line for markdown table)
    # Remove all types of newlines, tabs, and | characters
    clean_summary = summary.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('|', ' ')
    # Collapse multiple spaces into one
    clean_summary = ' '.join(clean_summary.split())
    if len(clean_summary) > 150:
        clean_summary = clean_summary[:147] + "..."
        
    source_str = f"[{source_window}]({url})" if url else source_window
    
    log_entry = f"| {timestamp} | [[{topic}]] | {clean_summary} | {source_str} |\n"
    
    with open(history_file, 'a', encoding='utf-8') as f:
        # Move to end of file and ensure we aren't appending to the middle of a line
        f.seek(0, 2) 
        f.write(log_entry)
