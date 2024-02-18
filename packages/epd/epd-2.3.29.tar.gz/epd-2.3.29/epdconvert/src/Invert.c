#define PY_SSIZE_T_CLEAN
#include <Python.h>


PyObject* invert(PyObject* self, PyObject *args, PyObject *keywds)
{
    unsigned char *in;
    unsigned char *out;
    unsigned long ptr;
    unsigned long outsize;
    Py_ssize_t insize;

    PyObject* result;

    static char *kwlist[] = {"data", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#", kwlist, &in, &insize)) return NULL;

    outsize = insize;
    out = malloc( outsize );

    ptr=0;

    while (ptr<insize) {
        out[ptr]=~in[ptr];
        ptr++;
    }

    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, outsize);
    #else
    result = Py_BuildValue("s#", out, outsize);
    #endif

    free(out);
    return result;
}
