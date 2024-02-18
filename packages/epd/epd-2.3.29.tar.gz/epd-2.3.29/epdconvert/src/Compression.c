#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "lz.h"

PyObject* compress_lz(PyObject* self, PyObject *args, PyObject *keywds)
{
   unsigned char *in;
   unsigned char *out;
   Py_ssize_t insize;
   int outpos;

   PyObject* result;

   static char *kwlist[] = {"data", NULL};

   if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#", kwlist, &in, &insize)) return NULL;

   out = malloc( (unsigned int) ((float)insize*1.5) ); // docs says 0.4+1, but ...
   outpos = LZ_Compress(in, out, insize);

    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, outpos);
    #else
    result = Py_BuildValue("s#", out, outpos);
    #endif

   free(out);
   return result;
}

PyObject* compress_rle(PyObject* self, PyObject *args, PyObject *keywds)
{
   unsigned char *in;
   unsigned char *out;
   Py_ssize_t insize, in_ptr, out_ptr;

   unsigned char counting_for_bit, current_bit, counter, bit_pos;

   PyObject* result;

   static char *kwlist[] = {"data", NULL};

   if (!PyArg_ParseTupleAndKeywords(args, keywds, "s#", kwlist, &in, &insize)) return NULL;

   out = malloc( insize*8 ); // can blow up to 1 byte per bit ...

    in_ptr=0;
	out_ptr=0;
	counting_for_bit = (in[in_ptr]&0x80)?1:0;
	bit_pos = 6;
	counter=0;
	while ( in_ptr<insize ) {

		for(int i=bit_pos;i>=0;i--) {

			current_bit = (in[in_ptr]&(0x01<<i))?1:0;

			if ((current_bit!=counting_for_bit) || (counter==127) ){
				out[out_ptr++] = ((counting_for_bit)?0x01:0x00) | (counter<<1);
				counter = 0;
				counting_for_bit = current_bit;
			} else {
				counter++;
			}
		}
		bit_pos=7;
		in_ptr++;
	}
	out[out_ptr++] = ((counting_for_bit)?0x01:0x00) | (counter<<1);


    #if PY_MAJOR_VERSION >= 3
    result = Py_BuildValue("y#", out, out_ptr);
    #else
    result = Py_BuildValue("s#", out, out_ptr);
    #endif

   free(out);
   return result;
}
