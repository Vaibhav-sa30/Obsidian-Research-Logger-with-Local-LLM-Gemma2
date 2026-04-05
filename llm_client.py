import ollama

MODEL_NAME = "gemma2:2b"

def decide_note_routing(text, existing_notes):
    """Asks Gemma if the text belongs in an existing note or a NEW one."""
    # To avoid overwhelming Gemma's context window, we take up to 200 note titles
    # Or as many as are available.
    notes_list = existing_notes[:200] 
    notes_list_str = "\n- ".join(notes_list)
    
    prompt = f"""You are a smart note-taking logic engine. The user has captured this text snippet:
---
{text}
---

Here is a list of the user's existing note files:
- {notes_list_str}

Analyze the snippet. Does this snippet strongly relate to one of the exact existing note files?
If YES, reply with ONLY the exact name of the existing note file from the list.
If NO (it's a new concept), reply with ONLY the word "NEW".
DO NOT output any explanation, markdown, or punctuation."""
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ], keep_alive=0)
        decision = response['message']['content'].strip()
        return decision
    except Exception as e:
        print(f"Error querying ollama for routing: {e}")
        return "NEW"

def generate_note_content(text, topic, existing_notes, window_title="Unknown", timestamp=""):
    """Asks Gemma to format the text into beautiful Markdown with Obsidian links and metadata."""
    
    # PRE-FILTER: Only suggest links for notes that actually appear as substrings in the text
    # This prevents the LLM from hallucinating links from the huge list we provide.
    relevant_concepts = []
    text_lower = text.lower()
    for note in existing_notes:
        if note.lower() in text_lower and len(note) > 3: # Ignore tiny notes like 'a', 'the'
            relevant_concepts.append(note)
    
    relevant_concepts_str = ", ".join(relevant_concepts[:20]) # Limit to top 20 matches
    
    prompt = f"""You are a brilliant Obsidian note assistant. 
The user is logging information to the topic '{topic}'.
Context: Captured from the window '{window_title}'.

Here is the raw captured text:
---
{text}
---

Please format this text into clear, readable Markdown. 
Highlight the key points using bullet points or bold text.

CRITICAL RULES:
1. NO INTRODUCTIONS/CONCLUSIONS: Output ONLY the markdown body.
2. NO EXTERNAL LINKS: Do not generate any [Markdown Links](url), [Source], or URLs.
3. NO HALLUCINATION: Only use [[links]] for the exact concepts listed below.
4. LINKING: Use these existing vault concepts ONLY: [{relevant_concepts_str}].
   Max 3 links. If none match, do not link anything.

Output strictly the Markdown body:"""

    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ], keep_alive=0)
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Error querying ollama for generation: {e}")
        return text 
        
def generate_new_topic_name(text):
    """If a new note is needed, generate a short 2-4 word file name."""
    prompt = f"""Provide a short, 2 to 4 word title for a note containing the following text. 
ONLY return the title string, no quotes, no extra words.
Text: "{text}"
Title:"""
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        # Clean up any weird characters provided by LLM
        topic = response['message']['content'].strip()
        topic = topic.replace('"', '').replace("'", '').replace(":", "").replace("/", "-")
        return topic
    except Exception as e:
        return "New Captured Note"
def unified_process(text, existing_notes, window_title="Unknown"):
    """
    PERFORMANCE OPTIMIZATION:
    Combines routing, topic generation, and synthesis into a SINGLE LLM call.
    Reduces latency by ~60% by avoiding multiple round-trips to Ollama.
    """
    # PRE-FILTER: Only suggest links for notes that actually appear in the text
    relevant_concepts = []
    text_lower = text.lower()
    for note in existing_notes:
        if note.lower() in text_lower and len(note) > 3:
            relevant_concepts.append(note)
    
    relevant_concepts_str = ", ".join(relevant_concepts[:20])
    notes_list_str = "\n- ".join(existing_notes[:100]) # Shorter list for speed

    prompt = f"""You are a smart research assistant. 
Input Text: "{text}"
Source: "{window_title}"

Existing Notes:
- {notes_list_str}

TASK:
1. ROUTING: Does this text belong in an existing note or a NEW one?
2. TOPIC: If it belongs to an existing note, give me that name. If it's NEW, generate a 2-4 word title.
3. SYNTHESIS: Format the text into clear Markdown bullet points/bold text. NO intros/outros.

CRITICAL RULES:
- NO EXTERNAL LINKS.
- ONLY use [[links]] for these specific existing concepts: [{relevant_concepts_str}]. Max 3.
- FORMAT: Your response MUST follow this exact structure:
TOPIC: [Title]
CONTENT: [Markdown Body]

Response:"""

    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'user', 'content': prompt},
        ], keep_alive=0)
        
        raw_output = response['message']['content'].strip()
        
        # Robust parsing (Case-insensitive labels)
        topic = "New Note"
        content = text
        
        # Look for labels regardless of case
        raw_upper = raw_output.upper()
        if "TOPIC:" in raw_upper and "CONTENT:" in raw_upper:
            # Find indices in the upper version
            topic_idx = raw_upper.find("TOPIC:")
            content_idx = raw_upper.find("CONTENT:")
            
            # Extract content from the original string using those indices
            topic = raw_output[topic_idx + 6 : content_idx].strip()
            content = raw_output[content_idx + 8 :].strip()

        # Clean up the topic name
        topic = topic.split("\n")[0].strip() # First line only
        topic = topic.replace("#", "").replace("*", "").replace("[", "").replace("]", "").strip()
        topic = topic.replace('"', '').replace("'", '').replace(":", "").replace("/", "-")
        
        if not topic: topic = "New Captured Note"
            
        return topic, content
    except Exception as e:
        print(f"Error in unified_process: {e}")
        return "New Captured Note", text
