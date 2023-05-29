class Matrix {
    constructor(rows, cols) {
        this.rows = rows;
        this.cols = cols;
        this.data = Array(rows).fill().map(() => Array(cols).fill(0));
    }

    static fromArray(arr) {
        return new Matrix(arr.length, 1).map((e, i) => arr[i]);
    }

    static subtract(a, b) {
        if (a.rows !== b.rows || a.cols !== b.cols) {
            throw new Error('Columns and Rows of A must match Columns and Rows of B.');
        }
        return new Matrix(a.rows, a.cols)
            .map((_, i, j) => a.data[i][j] - b.data[i][j]);
    }

    toArray() {
        let arr = [];
        this.map(v => arr.push(v));
        return arr;
    }

    randomize() {
        return this.map(_ => Math.random() * 2 - 1);
    }

    add(n) {
        if (n instanceof Matrix) {
            if (this.rows !== n.rows || this.cols !== n.cols) {
                throw new Error('Columns and Rows of A must match Columns and Rows of B.');
            }
            return this.map((e, i, j) => e + n.data[i][j]);
        } else {
            return this.map(e => e + n);
        }
    }

    multiply(n) {
        if (n instanceof Matrix) {
            // Element-wise multiply, also known as Hadamard product
            if (this.rows !== n.rows || this.cols !== n.cols) {
                throw new Error('Matrices must have the same dimensions for element-wise multiplication');
            }

            for (let i = 0; i < this.rows; i++) {
                for (let j = 0; j < this.cols; j++) {
                    this.data[i][j] *= n.data[i][j];
                }
            }
        } else {
            // Scalar multiplication
            for (let i = 0; i < this.rows; i++) {
                for (let j = 0; j < this.cols; j++) {
                    this.data[i][j] *= n;
                }
            }
        }

        return this;
    }

    static multiply(a, b) {
        // Matrix product
        if (a.cols !== b.rows) {
            throw new Error('Columns of A must match rows of B.');
        }
        return new Matrix(a.rows, b.cols)
            .map((e, i, j) => {
                let sum = 0;
                for (let k = 0; k < a.cols; k++) {
                    sum += a.data[i][k] * b.data[k][j];
                }
                return sum;
            });
    }

    static transpose(matrix) {
        return new Matrix(matrix.cols, matrix.rows)
            .map((_, i, j) => matrix.data[j][i]);
    }

    map(func) {
        // Apply a function to every element of matrix
        this.data = this.data.map((row, i) =>
            row.map((value, j) => func(value, i, j))
        );
        return this;
    }

    static map(matrix, func) {
        // Apply a function to every element of matrix
        return new Matrix(matrix.rows, matrix.cols)
            .map((e, i, j) => func(matrix.data[i][j], i, j));
    }

    static append(matrix1, matrix2) {
        if (matrix1.rows !== matrix2.rows) {
            throw new Error('Rows mismatch');
        }

        let result = new Matrix(matrix1.rows, matrix1.cols + matrix2.cols);

        for (let i = 0; i < result.rows; i++) {
            for (let j = 0; j < result.cols; j++) {
                if (j < matrix1.cols) {
                    result.data[i][j] = matrix1.data[i][j];
                } else {
                    result.data[i][j] = matrix2.data[i][j - matrix1.cols];
                }
            }
        }

        return result;
    }

    static appendColumn(matrix, column) {
        if (matrix.rows !== column.rows) {
            throw new Error('Rows mismatch');
        }

        let result = new Matrix(matrix.rows, matrix.cols + 1);

        for (let i = 0; i < result.rows; i++) {
            for (let j = 0; j < result.cols; j++) {
                if (j < matrix.cols) {
                    result.data[i][j] = matrix.data[i][j];
                } else {
                    result.data[i][j] = column.data[i][0];
                }
            }
        }

        return result;
    }

    static appendRow(matrix, row) {
        if (matrix.cols !== row.cols) {
            throw new Error('Columns mismatch');
        }

        let result = new Matrix(matrix.rows + 1, matrix.cols);

        for (let i = 0; i < result.rows; i++) {
            for (let j = 0; j < result.cols; j++) {
                if (i < matrix.rows) {
                    result.data[i][j] = matrix.data[i][j];
                } else {
                    result.data[i][j] = row.data[0][j];
                }
            }
        }

        return result;
    }

}