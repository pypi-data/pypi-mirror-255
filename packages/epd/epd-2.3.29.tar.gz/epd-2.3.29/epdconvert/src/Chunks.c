#define PY_SSIZE_T_CLEAN
#include <Python.h>


enum logtypes {info, warning, error, debug};

static void log_msg(int type, char *msg)
{
    static PyObject *logging = NULL;
    static PyObject *string = NULL;

    // import logging module on demand
    if (logging == NULL){
        logging = PyImport_ImportModuleNoBlock("logging");
        if (logging == NULL)
            PyErr_SetString(PyExc_ImportError,
                "Could not import module 'logging'");
    }

    // build msg-string
    string = Py_BuildValue("s", msg);

    // call function depending on loglevel
    switch (type)
    {
        case info:
            PyObject_CallMethod(logging, "info", "O", string);
            break;

        case warning:
            PyObject_CallMethod(logging, "warn", "O", string);
            break;

        case error:
            PyObject_CallMethod(logging, "error", "O", string);
            break;

        case debug:
            PyObject_CallMethod(logging, "debug", "O", string);
            break;
    }
    Py_DECREF(string);
}

void get_data_chunks(PyObject* self, PyObject *args, PyObject *keywds)
{

    Py_ssize_t insize;
    int i;
    PyObject* result;
    PyObject* list_in;

    static char *kwlist[] = {"chunks", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!", kwlist, &PyList_Type, &list_in)) return NULL;

    return NULL;

}
