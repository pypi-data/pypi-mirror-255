#include <stdio.h>
#include <Python.h>
#include "libpcio.h"

static void print_str(int w, int p, PyObject *o) {
  int fmt_kind;
  Py_ssize_t fmt_len,j;
  void *fmt;
  fmt_kind=PyUnicode_KIND(o);
  fmt=PyUnicode_DATA(o);
  fmt_len=PyUnicode_GET_LENGTH(o);
  Py_UCS4 c;
  for(j=0;j<fmt_len;++j) {
     c=PyUnicode_READ(fmt_kind,fmt,j);
     putchar(c);
  }
}
static void print_0(char fmt, int w, int p, PyObject *o) {
   if(PyList_Check(o)) {
     Py_ssize_t n=PyList_GET_SIZE(o);
     Py_ssize_t j;
     for(j=0;j<n;++j) {
       if(j>0) putchar(' ');
       print_0(fmt,w,p,PyList_GET_ITEM(o, j));
     }
     return;
   }
   if(PyTuple_Check(o)) {
     Py_ssize_t n=PyTuple_GET_SIZE(o);
     Py_ssize_t j;
     for(j=0;j<n;++j) {
       if(j>0) putchar(' ');
       print_0(fmt,w,p,PyTuple_GET_ITEM(o, j));
     }
     return;
   }
   if(PyUnicode_Check(o)) 
     print_str(w,p,o);
   else {
     PyObject *obj=PyObject_Str(o);
     print_str(w,p,obj);
     Py_DECREF(obj);
   }
}
PyObject* print(PyObject *self, PyObject *args) {
    Py_ssize_t argc=0;
    if(PyTuple_Check(args))
       argc=PyTuple_GET_SIZE(args);
    if(argc==0) Py_RETURN_NONE;
    Py_ssize_t n=1;
    PyObject *obj = PyTuple_GET_ITEM(args, 0);
    int fmt_kind;
    Py_ssize_t fmt_len,j;
    void *fmt=NULL;
    if(PyUnicode_Check(obj)) { // format
       fmt_kind=PyUnicode_KIND(obj);
       fmt=PyUnicode_DATA(obj);
       fmt_len=PyUnicode_GET_LENGTH(obj);
       Py_UCS4 c;
       for(j=0;j<fmt_len;++j) {
         c=PyUnicode_READ(fmt_kind,fmt,j);
         if(c=='{') {
           ++j;
           if(j<fmt_len) { 
             c=PyUnicode_READ(fmt_kind,fmt,j);
             if(c=='{')
               putchar('{');
             else {
               while(j<fmt_len) { 
                 c=PyUnicode_READ(fmt_kind,fmt,j);
                 if(c=='}') break;
               }
               if(n<argc) {
                 print_0(0,0,0,PyTuple_GET_ITEM(args, n));
                 ++n;
               }
             }
           }
         }
         else if(c=='}') {
           ++j;
           if(j<fmt_len) {
             c=PyUnicode_READ(fmt_kind,fmt,j);
             if(c=='}')
               putchar('}');
           }
         }
         else {
           putchar(c);
         }
       }
    }
    else {
      for(n=0;n<argc;++n) {
        if(n>0) putchar(' ');
        print_0(0,0,0,PyTuple_GET_ITEM(args, n));
      }
    }
    Py_RETURN_NONE;
}
PyObject* println(PyObject *self, PyObject *args) {
  print(self,args);
  putchar('\n');
  Py_RETURN_NONE;
}
