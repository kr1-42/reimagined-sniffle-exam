def pattern_tracker(text: str) -> int:

    conteggio = 0
    
    for i in range(len(text) - 1):
        carattere_sinistro = text[i]
        carattere_destro = text[i + 1]
        
        if carattere_sinistro.isdigit() and carattere_destro.isdigit():
            
            numero_sinistro = int(carattere_sinistro)
            numero_destro = int(carattere_destro)
            
            if numero_destro == numero_sinistro + 1:
                conteggio += 1
                
    return conteggio