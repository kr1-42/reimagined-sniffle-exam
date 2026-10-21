def inter(s1: str, s2: str) -> str:

    risultato = ""
    
    for c in s1:
        if c in s2 and c not in risultato:
            risultato += c
            
    return risultato