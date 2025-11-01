import yaml

# Load YAML from a file
with open("adjusted_ifr.yaml", "r") as f:
    data = yaml.safe_load(f)

# Print the structure

# Example: access the IFR Score of the first ATC-I item
#first_item_ifr = data["ATC-I"]["1. Presence of animals or people on aerodrome"]["IFR Score"]
#print("First ATC-I IFR Score:", first_item_ifr)

total_ifr = 0

# Get the ATC-I questions
atc_i_questions = data.get("UNICOM-V", {})

for question_text, scores in atc_i_questions.items():
    print(scores)
    if 1 in scores:  # Answer 2
        try:
            print(scores)
            total_ifr += float(scores[1])
        except ValueError:
            print(f"Skipping non-numeric IFR for question '{question_text}'")

print("Total IFR Score for answer 2 in ATC-I:", total_ifr)


