#define PY_SSIZE_T_CLEAN
#include <Python.h>


uint32_t crc32_for_byte(uint32_t r)
{
  for(int j = 0; j < 8; ++j)
    r = (r & 1? 0: (uint32_t)0xEDB88320L) ^ r >> 1;
  return r ^ (uint32_t)0xFF000000L;
}

void crc32_internal(const void *data, size_t n_bytes, uint32_t* crc)
{
  static uint32_t table[0x100];
  if(!*table)
    for(size_t i = 0; i < 0x100; ++i)
      table[i] = crc32_for_byte(i);
  for(size_t i = 0; i < n_bytes; ++i)
    *crc = table[(uint8_t)*crc ^ ((uint8_t*)data)[i]] ^ *crc >> 8;
}


PyObject* crc32(PyObject* self, PyObject *args, PyObject *keywds)
{
    unsigned char *in;
    unsigned char *out;

    Py_ssize_t insize;

    PyObject* result;

    unsigned char crc32result[4];

    static char *kwlist[] = {"data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#", kwlist, &in, &insize )) return NULL;

    crc32_internal(in, insize, &crc32result);


    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", &crc32result, 4);
    #else
    result = Py_BuildValue("s#", &crc32result, 4);
    #endif

    free(out);
    return result;
}
