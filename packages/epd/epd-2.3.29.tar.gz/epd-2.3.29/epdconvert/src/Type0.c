#define PY_SSIZE_T_CLEAN
#include <Python.h>


PyObject* convertToType0_1bit(PyObject* self, PyObject *args, PyObject *keywds)
{
    unsigned char *in;
    unsigned char *out;
    unsigned long in_ptr;
    unsigned long outsize, out_ptr;
    Py_ssize_t insize;
    unsigned char i,n;

    PyObject* result;

    static char *kwlist[] = {"data", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#", kwlist, &in, &insize)) return NULL;

    outsize = insize/8;
    out = malloc( outsize );

    in_ptr=0;
    out_ptr=0;

    while (in_ptr<insize) {
        n=0;
        for ( i=0; i<8; i++ ) {
            if (in[in_ptr]>0) n = n | (0x80>>i);
            in_ptr++;
        }
        out[out_ptr++]=n;
    }

    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, outsize);
    #else
    result = Py_BuildValue("s#", out, outsize);
    #endif

    free(out);
    return result;
}

PyObject* convertToType0_2bit(PyObject* self, PyObject *args, PyObject *keywds)
{
    unsigned char *in;
    unsigned char *out;
    unsigned long in_ptr;
    unsigned int line_length, line_length_bytes;
    unsigned long outsize, out_ptr;
    unsigned char i,n_lsb,n_msb;
    Py_ssize_t insize;

    PyObject* result;

    static char *kwlist[] = {"data", "line_length", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#i", kwlist, &in, &insize,&line_length)) return NULL;

    line_length_bytes = line_length/8;

    outsize = insize/4;
    out = malloc( outsize );

    in_ptr=0;
    out_ptr=0;

    while (in_ptr<insize) {
        n_lsb=0;
        n_msb=0;
        for ( i=0; i<8; i++ ) {
            if ( (in[in_ptr] & 0x01)>0) n_lsb = n_lsb | (0x80>>i);
            if ( (in[in_ptr] & 0x02)>0) n_msb = n_msb | (0x80>>i);
            in_ptr++;
        }

        out[out_ptr]=n_lsb;
        out[line_length_bytes+out_ptr]=n_msb;
        out_ptr++;
        if ((out_ptr % line_length_bytes) == 0) out_ptr+=line_length_bytes;
    }

    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, outsize);
    #else
    result = Py_BuildValue("s#", out, outsize);
    #endif

    free(out);
    return result;
}
