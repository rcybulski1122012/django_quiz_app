def is_too_long_word_in_text(text, max_length=45):
    words_lengths = [len(word) for word in text.split()]
    for length in words_lengths:
        if length > max_length:
            return True
    return False
