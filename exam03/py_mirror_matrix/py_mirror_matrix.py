
def mirror_matrix(matrix: list[list[int]]) -> list[list[int]]:

    return [riga[::-1] for riga in matrix]