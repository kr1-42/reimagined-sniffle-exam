def string_sculptor(text: str) -> str:
    risultato = ""
    
    maiuscolo = False 
    
    for c in text:
        
        if c == " ":
            risultato += c
            maiuscolo = False
            
        elif c.isalpha():
            if maiuscolo:
                risultato += c.upper()
            else:
                risultato += c.lower()

            maiuscolo = not maiuscolo

        else:
            risultato += c
            
    return risultato