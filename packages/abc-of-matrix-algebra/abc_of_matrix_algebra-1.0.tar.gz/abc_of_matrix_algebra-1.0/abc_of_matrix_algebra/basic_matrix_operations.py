# a package to compute basic matrix operations

def matrix_addition(matrix1, matrix2):
    """Perform matrix addition."""
    if len(matrix1) != len(matrix2) or len(matrix1[0]) != len(matrix2[0]):
        raise ValueError("Matrices must have the same dimensions for addition.")
    result = [[matrix1[i][j] + matrix2[i][j] for j in range(len(matrix1[0]))] for i in range(len(matrix1))]
    return result

def matrix_subtraction(matrix1, matrix2):
    """Perform matrix subtraction."""
    if len(matrix1) != len(matrix2) or len(matrix1[0]) != len(matrix2[0]):
        raise ValueError("Matrices must have the same dimensions for subtraction.")
    result = [[matrix1[i][j] - matrix2[i][j] for j in range(len(matrix1[0]))] for i in range(len(matrix1))]
    return result

def matrix_multiplication(matrix1, matrix2):
    """Perform matrix multiplication."""
    if len(matrix1[0]) != len(matrix2):
        raise ValueError("Number of columns in the first matrix must equal the number of rows in the second matrix for multiplication.")
    result = [[sum(matrix1[i][k] * matrix2[k][j] for k in range(len(matrix2))) for j in range(len(matrix2[0]))] for i in range(len(matrix1))]
    return result
