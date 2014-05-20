#include <Python.h>

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)))

static PyObject * distance_py(PyObject *self, PyObject *args) {
    // Code from https://en.wikibooks.org/
    // wiki/Algorithm_Implementation/Strings/Levenshtein_distance
    char *s1, *s2;
    long int x, y, s1len, s2len;

    if (!PyArg_ParseTuple(args, "ss", &s1, &s2)) {
        return NULL;
    }

    s1len = strlen(s1);
    s2len = strlen(s2);
    long int matrix[s2len + 1][s1len + 1];
    matrix[0][0] = 0;
    for (x = 1; x <= s2len; x++) {
        matrix[x][0] = matrix[x - 1][0] + 1;
    }
    for (y = 1; y <= s1len; y++) {
        matrix[0][y] = matrix[0][y - 1] + 1;
    }
    for (x = 1; x <= s2len; x++) {
        for (y = 1; y <= s1len; y++) {
            matrix[x][y] = MIN3(
                matrix[x - 1][y] + 1,
                matrix[x][y - 1] + 1,
                matrix[x - 1][y - 1] + (s1[y - 1] == s2[x - 1] ? 0 : 1)
            );
        }
    }

    return PyInt_FromLong((long)matrix[s2len][s1len]);
}

static PyMethodDef LevenshteinMethods[] = {
    {"distance",  distance_py, METH_VARARGS, "Levenshtein distance."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initlevenshtein(void) {
    (void) Py_InitModule("levenshtein", LevenshteinMethods);
}
