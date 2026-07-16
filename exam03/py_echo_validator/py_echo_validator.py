def echo_validator(text: str) -> bool:

    spulita = "" 
    
    for c in text: 
        if c.isalpha():
            spulita += c.lower()

    if not spulita:
        return False

    return(spulita == spulita[::-1])


print(echo_validator("A man a plan a canal Panama"))