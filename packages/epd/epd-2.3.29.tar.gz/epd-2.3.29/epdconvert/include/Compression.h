#ifndef COMPRESSION
#define COMPRESSION

PyObject* compress_lz(PyObject* self, PyObject *args, PyObject *keywds);
PyObject* compress_rle(PyObject* self, PyObject *args, PyObject *keywds);
#endif