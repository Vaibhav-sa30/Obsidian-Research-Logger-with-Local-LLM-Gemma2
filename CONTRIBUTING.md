# Contributing to Intelligent Obsidian Logger 

Thank you for your interest in improving the Intelligent Obsidian Logger! Here is how you can help.

## Development Workflow

1. **Fork the repository** and clone it locally.
2. **Set up your environment** as described in the [README](README.md).
3. **Use the Launcher:** Always run `python launcher.py` while developing. It watches for file changes and restarts the service automatically, saving you from manual process management.

## Testing
- Test with various source applications (PDF Readers, Browsers, VS Code, etc.).
- Verify that URL capture works in Chrome, Edge, and Firefox.
- Check the `_Logger History.md` in your vault to ensure the markdown table remains valid.

## Ideas for Contribution
- **Prompt Engineering:** Improve `llm_client.py` for even better synthesis or tagging.
- **New Metadata:** Add support for more browser URL extraction methods.
- **UI Customization:** Allow users to configure the notification position or theme.
- **Cross-Platform Support:** Help us make the script work seamlessly on macOS and Linux (currently optimized for Windows).

## Guidelines
- Keep the project **privacy-first**: Do not add any external API calls unless they are optional and local.
- Follow **Single Responsibility Principle**: Keep `vault_manager.py`, `llm_client.py`, and `capture.py` focused on their respective tasks.
- Keep the `main.py` entry point clean.

Happy Coding! 
