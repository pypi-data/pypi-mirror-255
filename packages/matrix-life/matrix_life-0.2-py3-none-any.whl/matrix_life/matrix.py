from __future__ import annotations

from typing import Any, Sequence


class Matrix:
    def __init__(self, values: Sequence[Sequence]) -> None:
        assert_shape(values)
        self.matrix = [list(row) for row in values]
        self.num_rows = len(values)
        self.num_cols = len(values[0])

    def __add__(self, other: Matrix) -> Matrix:
        assert_same_shape(self, other)
        result = self.__copy__()

        for row_idx, row in enumerate(other.matrix):
            for col_idx, value in enumerate(row):
                result.matrix[row_idx][col_idx] += value

        return result

    def __sub__(self, other: Matrix) -> Matrix:
        assert_same_shape(self, other)
        result = self.__copy__()

        for row_idx, row in enumerate(other.matrix):
            for col_idx, value in enumerate(row):
                result.matrix[row_idx][col_idx] -= value

        return result

    def __mul__(self, other: Matrix) -> Matrix:
        assert_same_shape(self, other)
        result = self.__copy__()

        for row_idx, row in enumerate(other.matrix):
            for col_idx, value in enumerate(row):
                result.matrix[row_idx][col_idx] *= value

        return result

    def __truediv__(self, other: Matrix) -> Matrix:
        assert_same_shape(self, other)
        result = self.__copy__()

        for row_idx, row in enumerate(other.matrix):
            for col_idx, value in enumerate(row):
                result.matrix[row_idx][col_idx] /= value

        return result

    def __matmul__(self, other: Matrix) -> Matrix:
        assert_conformability(self, other)
        result = Matrix.full_of(self.num_rows, other.num_cols, 0)

        for row_idx in range(len(self.matrix)):
            for col_idx in range(len(other.matrix[0])):
                for elem_idx in range(len(other.matrix)):
                    product = self.matrix[row_idx][elem_idx] \
                              * other.matrix[elem_idx][col_idx]

                    result.matrix[row_idx][col_idx] += product

        return result

    def __pow__(self, power: int) -> Matrix:
        assert_square(self)

        if power == 0:
            return Matrix.identity(self.num_rows, self.num_cols)

        result = self.__copy__()

        for _ in range(power - 1):
            result @= self

        return result

    def __eq__(self, other: Matrix) -> bool:
        assert_same_shape(self, other)
        return self.matrix.__eq__(other.matrix)

    def __copy__(self) -> Matrix:
        return Matrix(self.matrix)

    def __repr__(self) -> str:
        return f'{self.num_rows} x {self.num_cols} matrix:\n' \
            + '\n'.join([str(row) for row in self.matrix])

    @classmethod
    def full_of(cls, num_rows: int, num_cols: int, value: Any) -> Matrix:
        return cls([[value for _ in range(num_cols)] for _ in range(num_rows)])

    @classmethod
    def identity(cls, num_rows: int, num_cols: int) -> Matrix:
        matrix = Matrix.full_of(num_rows, num_cols, 0)

        for idx in range(min(num_rows, num_cols)):
            matrix.matrix[idx][idx] = 1

        return matrix

    def transpose(self) -> Matrix:
        transposed = [[self.matrix[row_idx][col_idx]
                       for row_idx in range(self.num_rows)]
                      for col_idx in range(self.num_cols)]

        return Matrix(transposed)

    def is_symmetric(self) -> bool:
        assert_square(self)
        return self == self.transpose()


def assert_shape(values: Sequence[Sequence]) -> None:
    num_cols = len(values[0])

    for row in values:
        assert len(row) == num_cols, \
            f'Cannot create ragged matrix, ' \
            f'expected a consistent number of columns.'


def assert_square(matrix: Matrix) -> None:
    num_rows = matrix.num_rows
    num_cols = matrix.num_cols

    assert num_rows == num_cols, \
        f'Expected matrix to be square-shaped but got ' \
        f'shape: {num_rows} x {num_cols}.'


def assert_same_shape(matrix_1: Matrix, matrix_2: Matrix) -> None:
    num_rows_1 = matrix_1.num_rows
    num_rows_2 = matrix_2.num_rows

    assert num_rows_1 == num_rows_2, \
        f'Expected matrices to have the same shape but got ' \
        f'{num_rows_1} and {num_rows_2} rows respectively.'

    num_cols_1 = matrix_1.num_cols
    num_cols_2 = matrix_2.num_cols

    assert num_cols_1 == num_cols_2, \
        f'Expected matrices to have the same shape but got ' \
        f'{num_cols_1} and {num_cols_2} columns respectively.'


def assert_conformability(matrix_1: Matrix, matrix_2: Matrix) -> None:
    num_cols = matrix_1.num_cols
    num_rows = matrix_2.num_rows

    assert num_cols == num_rows, \
        f'Expected matrices to be conformable, but ' \
        f'matrix A has {num_cols} columns and matrix B has {num_rows} rows.'
