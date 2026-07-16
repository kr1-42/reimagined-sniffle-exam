def whisper_cipher(text: str, shift: int) -> str:
    risultato = ""
    
    for c in text:
        if c.isalpha():
            
            # Blocco if-else classico al posto dell'operatore ternario
            if c.isupper():
                base = 65
            else:
                base = 97
                
            # La formula matematica rimane esattamente la stessa
            risultato += chr((ord(c) - base + shift) % 26 + base)
            
        else:
            risultato += c
            
    return risultato