

def recompose_messages(query: str, history: List[Tuple[str, str]], system: str) -> List[ChatMessage]:
    messages = []

    # Add the system message, 暫時一律放在最前面 (因為react相關的好像暫時用不到system, 老實說這樣還是有點怪, 因為不respect客戶的順序)
    if system:
        messages.append(ChatMessage(role="system", content=system))

    # Recompose history messages
    for q, a in history:
        if q:  # Add user message if it exists
            messages.append(ChatMessage(role="user", content=q))
        if a:  # Add assistant message if it exists
            messages.append(ChatMessage(role="assistant", content=a))

    # Add the current query message
    # if query:
    # NOTE: modified by TS, if object()會是true
    if query and query is not _TEXT_COMPLETION_CMD:
        messages.append(ChatMessage(role="user", content=query))

    return messages

# To work around that unpleasant leading-\n tokenization issue!
def add_extra_stop_words(stop_words: List[str]):
    if stop_words:
        _stop_words = []
        _stop_words.extend(stop_words)
        for x in stop_words:
            s = x.lstrip('\n')
            if s and (s not in _stop_words):
                _stop_words.append(s)
        return _stop_words
    return stop_words