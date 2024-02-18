#define PY_SSIZE_T_CLEAN
#include <Python.h>


PyObject* flip_xy(PyObject* self, PyObject *args, PyObject *keywds)
{
    unsigned char *in;
    unsigned char *out;
    unsigned long outsize;
    unsigned int image_bytes_width;

    unsigned int xp, yp, height;
    unsigned char new_byte, old_byte, i, j;

    Py_ssize_t insize;

    PyObject* result;

    static char *kwlist[] = {"data", "image_bytes_width", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#I", kwlist, &in, &insize, &image_bytes_width)) return NULL;

    outsize = insize;
    out = malloc( outsize );

    height = insize/image_bytes_width;

    for ( yp=0; yp<height; yp++) {
        for ( xp=0; xp<image_bytes_width; xp++) {
            new_byte = 0;
            old_byte = in[yp*image_bytes_width+xp];

            for (i = 0, j = 7; i < 8; ++i, --j) {
                new_byte |= ((old_byte & (1 << j)) >> j) << i;
            }
            out[yp*image_bytes_width+(image_bytes_width-xp)] = new_byte;
        }
    }

    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, outsize);
    #else
    result = Py_BuildValue("s#", out, outsize);
    #endif

    free(out);
    return result;
}
