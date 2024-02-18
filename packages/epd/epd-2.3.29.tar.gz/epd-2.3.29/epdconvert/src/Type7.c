#define PY_SSIZE_T_CLEAN
#include <Python.h>


PyObject* convertToType7_1bit(PyObject* self, PyObject *args, PyObject *keywds)
{
    unsigned char *in;
    unsigned char *out;
    unsigned long in_ptr;
    unsigned long outsize, out_ptr;
    Py_ssize_t insize;

    PyObject* result;

    static char *kwlist[] = {"data", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#", kwlist, &in, &insize)) return NULL;

    outsize = insize/8;
    out = malloc( outsize );

    in_ptr=0;
    out_ptr=0;

    for ( in_ptr=0; in_ptr<insize; in_ptr+=16 ) {
        out[out_ptr]=0;
        if ( in[in_ptr+4]>0 )  out[out_ptr] |= 0x80;
        if ( in[in_ptr+12]>0 )  out[out_ptr] |= 0x40;
        if ( in[in_ptr+5]>0 )  out[out_ptr] |= 0x20;
        if ( in[in_ptr+13]>0 )  out[out_ptr] |= 0x10;
        if ( in[in_ptr+6]>0 )  out[out_ptr] |= 0x08;
        if ( in[in_ptr+14]>0 )  out[out_ptr] |= 0x04;
        if ( in[in_ptr+7]>0 )  out[out_ptr] |= 0x02;
        if ( in[in_ptr+15]>0 )  out[out_ptr] |= 0x01;

        out_ptr++;out[out_ptr]=0;
        if ( in[in_ptr]>0 )  out[out_ptr] |= 0x80;
        if ( in[in_ptr+8]>0 )  out[out_ptr] |= 0x40;
        if ( in[in_ptr+1]>0 ) out[out_ptr] |= 0x20;
        if ( in[in_ptr+9]>0 ) out[out_ptr] |= 0x10;
        if ( in[in_ptr+2]>0 ) out[out_ptr] |= 0x08;
        if ( in[in_ptr+10]>0 ) out[out_ptr] |= 0x04;
        if ( in[in_ptr+3]>0 ) out[out_ptr] |= 0x02;
        if ( in[in_ptr+11]>0 ) out[out_ptr] |= 0x01;


        out_ptr++;
    }

    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, outsize);
    #else
    result = Py_BuildValue("s#", out, outsize);
    #endif

    free(out);
    return result;
}
