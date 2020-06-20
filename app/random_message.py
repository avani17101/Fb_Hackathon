import random
def get_message():
    sample_responses = [
        "You are a dirty fellow!",
        "Of course I talk like an idiot. How else would u understand me?",
        "I made a pencil with two erasers. It was pointless.",
        "What's brown and sticky? A stick.",
    ]
    # return selected item to the user
    return random.choice(sample_responses)