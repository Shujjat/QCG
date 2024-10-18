import difflib


def compare_texts(text1, text2):
    # Split the paragraphs into lines
    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)

    # Create a Differ object and calculate differences
    diff = list(difflib.ndiff(lines1, lines2))

    # Prepare a list to store the interpreted result
    interpreted_result = []

    for i, line in enumerate(diff):
        # Check for deletions, insertions, and changes
        if line.startswith('-'):
            interpreted_result.append(f"Line {i+1}: Deleted -> {line[2:]}")
        elif line.startswith('+'):
            interpreted_result.append(f"Line {i+1}: Added -> {line[2:]}")
        elif line.startswith('?'):
            interpreted_result.append(f"Line {i}: Change Details -> {line[2:]}")

    return interpreted_result