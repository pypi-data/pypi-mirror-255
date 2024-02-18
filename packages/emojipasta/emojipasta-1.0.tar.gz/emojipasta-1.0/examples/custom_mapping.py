from emojipasta import Emojipasta
import json

with open("emoji-mappings-custom.json", "r", encoding="utf8") as f:
    mapping = json.load(f)

emoji = Emojipasta.of_custom_mappings(mapping)

print(emoji.generate_emojipasta(text="you are nice"))

# Output: you 😂 are 🙏🍑 nice 😍