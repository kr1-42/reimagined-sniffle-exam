def number_base_converter(number: str, from_base: int, to_base: int) -> str:

    if not (2 <= from_base <= 36 and 2 <= to_base <= 36):
        return "ERROR"
        
    try:
        n = int(number, from_base)
    except ValueError:
        return "ERROR"
        
    if n == 0:
        return "0"
        
    alfabeto = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    risultato = ""
    
    while n > 0:
        resto = n % to_base
        risultato += alfabeto[resto]
        n = n // to_base
        
    return risultato[::-1]