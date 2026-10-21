def cryptic_sorter(strings: list[str]) -> list[str]:
    
    def calcola_criteri(s: str):
        lunghezza = len(s)
        
        alfabetico_base = s.lower()
        
        numero_vocali = 0
        for c in alfabetico_base:  
            if c in "aeiou":         
                numero_vocali += 1
        
        return (lunghezza, alfabetico_base, numero_vocali, s)
        
    return sorted(strings, key=calcola_criteri)


print(cryptic_sorter(["apple","cat","banana","dog","elephant"]))
print(cryptic_sorter(["aaa","bbb","AAA","BBB"]))
print(cryptic_sorter(["hello","world","hi","test"]))
print(cryptic_sorter([]))
print(cryptic_sorter([""]))
