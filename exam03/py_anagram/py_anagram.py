def anagram(s1: str, s2: str) -> bool:
    s1_pulita = s1.replace(" ", "").lower()
    s2_pulita = s2.replace(" ", "").lower()
    
    return sorted(s1_pulita) == sorted(s2_pulita)