import pyperclip
import time
import keyboard
import pygetwindow as gw
import uiautomation as auto

def get_browser_url(window_title):
    """
    Attempts to extract the URL from Chrome, Edge, or Firefox using UI Automation.
    Does not interfere with the user's focus.
    """
    try:
        # Normalize title for common browsers
        title_lower = window_title.lower()
        if not any(b in title_lower for b in ["chrome", "edge", "firefox"]):
            return None

        # Get the browser window element
        browser_window = auto.WindowControl(searchDepth=1, Name=window_title)
        if not browser_window.Exists(0):
            return None

        # Strategy 1: Look for Address and search bar (most common in Chrome/Edge)
        url_control = browser_window.EditControl(searchDepth=10, Name="Address and search bar")
        if url_control.Exists(0):
            return url_control.GetValuePattern().Value
            
        # Strategy 2: Looking for generic Edit control in toolbar
        # (Fallbacks for different versions/locales)
        for edit in browser_window.GetChildren():
             if edit.ControlTypeName == "EditControl":
                 val = edit.GetValuePattern().Value
                 if val and (val.startswith("http") or "www." in val):
                     return val
    except:
        pass
    return None

def get_selected_text():
    """
    Simulates Ctrl+C to copy highlighted text to clipboard,
    then returns (text, window_title, url) and restores the old clipboard.
    """
    # Get active window title before switching focus (if any)
    url = None
    try:
        active_window = gw.getActiveWindow()
        window_title = active_window.title if active_window else "Unknown App"
        url = get_browser_url(window_title)
    except:
        window_title = "Unknown App"

    # Save current clipboard
    old_clipboard = pyperclip.paste()
    # Empty clipboard
    pyperclip.copy('')
    
    # Send Ctrl+C to copy selected text
    keyboard.send('ctrl+c')
    time.sleep(0.3) # Give Windows time to update the clipboard
    
    # Read new clipboard
    new_clipboard = pyperclip.paste()
    
    selected_text = new_clipboard
    
    # Restore old clipboard (optional, but good UX)
    if not new_clipboard:
        pyperclip.copy(old_clipboard)
        return "", window_title, url
        
    pyperclip.copy(old_clipboard)
    
    return selected_text, window_title, url
