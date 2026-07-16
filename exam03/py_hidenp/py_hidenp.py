def hidenp(small: str, big: str) -> bool:
    # Trasformiamo 'big' in un nastro trasportatore (iteratore)
    nastro_big = iter(big)
    
    # Controlliamo se OGNI carattere di 'small' si trova lungo il nastro (sempre andando avanti)
    return all(c in nastro_big for c in small)