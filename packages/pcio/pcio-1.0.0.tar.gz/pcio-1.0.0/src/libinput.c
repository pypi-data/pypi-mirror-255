#include <stdio.h>
#include <math.h>
#include <Python.h>
#include "libpcio.h"

char pcio_enc[32]="utf-8";
PyObject * encoding(PyObject* self, PyObject* args) {
  Py_ssize_t argc=0;
  if(PyTuple_Check(args))
    argc=PyTuple_GET_SIZE(args);
  if(argc==1) {
    PyObject *obj = PyTuple_GET_ITEM(args, 0);
    if(PyUnicode_Check(obj))
    {
       int fmt_kind;
       Py_ssize_t fmt_len,j;
       void *fmt;
       fmt_kind=PyUnicode_KIND(obj);
       fmt=PyUnicode_DATA(obj);
       fmt_len=PyUnicode_GET_LENGTH(obj);
       for(j=0;j<fmt_len && j<31;++j)
         pcio_enc[j]=PyUnicode_READ(fmt_kind,fmt,j);
       pcio_enc[j]='\0';
    }
  }
  Py_RETURN_NONE;
}
static char *line=NULL, *p_line;
static size_t line_len=0,line_maxlen=0;
static char *buf;
static int line_eof=0;
static void getline(char eoln) {
  const size_t MINBUF=65536;
  if(line==NULL) {
    buf=malloc(MINBUF);
    setvbuf(stdin,buf,_IOFBF,MINBUF);
    line=malloc(line_maxlen=MINBUF);
    line[line_len=0]='\0';
    p_line=line;
  }
  if(*p_line=='\0') {
    p_line=line;
    line_len=0;
  }
  for(;;) {
    if(line_maxlen-line_len<MINBUF) {
      line_maxlen*=2;
      size_t pos=p_line-line;
      line=realloc(line,line_maxlen);
      p_line=line+pos;
    }
    if(!fgets(line+line_len,(int)(line_maxlen-line_len),stdin)) {
      line_eof=1;
      line[line_len]='\0';
      return;
    }
    line_len+=strlen(line+line_len);
    if(line_len>0 && line[line_len-1]==eoln) { 
      if(line_len>1 && line[line_len-2]=='\r') {
        --line_len;
        line[line_len-1]=line[line_len];
        line[line_len]='\0';
      }
      return; 
    }
  }
}
static void skipws(void) {
  if(!line) getline('\n');
  while(!(*p_line=='\0' && line_eof)) {
    while(*p_line>0 && *p_line<=' ')
      ++p_line;
    if(*p_line) return;
    getline('\n');
  }
}
PyObject* input_int(PyObject * self) {
  skipws();
  if(*p_line=='\0' && line_eof)
    Py_RETURN_NONE;
  int minus=0,k=0;
  char *start=p_line, *end;
  if(*p_line=='-') {
    minus=1;
    ++p_line;
  }
  long long x=0;
  int c;
  while((c=*p_line)>='0' && c<='9') { 
    x=x*10+(c-'0');
    ++k;
    ++p_line;
  }
  if(k==0) {
    if(minus) --p_line;
    return PyFloat_FromDouble(NAN);
  }
  else if(k<19)
    return PyLong_FromLongLong(minus?-x:x);
  else {
    PyObject* obj;
    c=*p_line;
    *p_line='\0';
    obj=PyLong_FromString(start,&end,10);
    *p_line=c;
    return obj;
  }
}
PyObject* input_float(PyObject * self) {
  skipws();
  if(*p_line=='\0' && line_eof)
    Py_RETURN_NONE;
  char *end;
  double x=strtod(p_line,&end);
  if(p_line==end)
    return PyFloat_FromDouble(NAN);
  else
  { p_line=end;
    return PyFloat_FromDouble(x);
  }
}
static PyObject* input_0(int mode)
{
  if(mode=='w') skipws();
  else if(!line || *p_line=='\0' && !line_eof) getline('\n');
  if(*p_line=='\0' && line_eof)
    Py_RETURN_NONE;
  if(!line_eof && mode=='a')
    getline(0);
  size_t len=line+line_len-p_line;
  if(mode=='a' || mode=='L')
    ;
  else if(mode=='l') {
    if(p_line[len-1]=='\n')
      p_line[--len]='\0';
  }
  else if(mode=='c') {
    len=1;
    if(pcio_enc[0]=='u') {
      if((p_line[0]&0x80)==0) ;
      else if((p_line[0]&0xE0)==0xC0 && (p_line[1]&0xC0)==0x80) len=2;
      else if((p_line[0]&0xF0)==0xE0 && (p_line[1]&0xC0)==0x80 && (p_line[2]&0xC0)==0x80) len=3;
      else if((p_line[0]&0xF8)==0xF0 && (p_line[1]&0xC0)==0x80 && (p_line[2]&0xC0)==0x80 && (p_line[3]&0xC0)==0x80) len=4;
    }
  }
  else { // mode=='w'
    for(len=0;p_line[len]>0 && p_line[len]<=' ';++len)
      ;
  }
  PyObject* ret = PyUnicode_Decode(p_line,len,pcio_enc,"replace");
  p_line+=len;
  return ret;
}
PyObject* input_line(PyObject * self) {
  return input_0('l');
}
PyObject* input_word(PyObject * self) {
  return input_0('w');
}
PyObject* input_char(PyObject * self) {
  return input_0('c');
}

static PyObject* input_1(int mode) {
  if(mode=='f')
    return input_float(NULL);
  else if(mode=='i')
    return input_int(NULL);
  else
    return input_0(mode);
}
static PyObject* input_2(int fmt_kind, Py_ssize_t fmt_len, void *fmt, int fmt_c) {
   PyObject* ret;
   if(fmt_c>1) {
     ret=PyTuple_New(fmt_c);
   }
   else if(fmt_c==0) {
      Py_RETURN_NONE;
   }
   int k=0;
   for(Py_ssize_t j=0;j<fmt_len;++j) {
     unsigned char mode=PyUnicode_READ(fmt_kind,fmt,j);
     if(strchr("cifwlLa",mode)) {
       PyObject* obj=input_1(mode);
       if(fmt_c==1)
         return obj;
       PyTuple_SET_ITEM(ret, k++, obj);
     }
   }    
   return ret;
}

PyObject * input(PyObject *self, PyObject *args) {
    PyObject * ret;
    Py_ssize_t argc=0;
    if(PyTuple_Check(args))
       argc=PyTuple_GET_SIZE(args);
    long count_c=-1;
    int fmt_c=1;
    int fmt_kind=-1;
    int fmt_mode='l';
    Py_ssize_t fmt_len=0;
    void *fmt=NULL;
    if(argc>0) {
      int n=0;
      PyObject *obj = PyTuple_GET_ITEM(args, 0);
      if(PyLong_Check(obj)) {
        count_c=PyLong_AsLong(obj);
        if(count_c<0) count_c=0;
        n++;
      }
      if(n<argc) {
         obj = PyTuple_GET_ITEM(args, n);
         if(PyUnicode_Check(obj)) {
           fmt_kind=PyUnicode_KIND(obj);
           fmt=PyUnicode_DATA(obj);
           fmt_len=PyUnicode_GET_LENGTH(obj);
           fmt_c=0;
           for(Py_ssize_t j=0;j<fmt_len;++j) {
             unsigned char mode=PyUnicode_READ(fmt_kind,fmt,j);
             if(strchr("cifwlLa",mode))
             { fmt_mode=mode;
               fmt_c++;
             }
           }
	 }
      }
      else if(n>0) {
        fmt_mode='c';
        fmt_c=1;
      }
    }
    if(count_c>=0 && fmt_c==1 && fmt_mode=='c') {
       if(!line || *p_line=='\0' && !line_eof) getline('\n');
       if(*p_line=='\0' && line_eof)
         Py_RETURN_NONE;
       size_t len=0,n=0;
       while(n<count_c)
       { 
         if(p_line[len]=='\0' && line_eof) break;
         if(p_line[len]=='\0') getline('\n');
         if(p_line[len]=='\0' && line_eof) break;
         if(pcio_enc[0]=='u') {
            if((p_line[0]&0x80)==0) ;
            else if((p_line[0]&0xE0)==0xC0 && (p_line[1]&0xC0)==0x80) ++len;
            else if((p_line[0]&0xF0)==0xE0 && (p_line[1]&0xC0)==0x80 && (p_line[2]&0xC0)==0x80) len+=2;
            else if((p_line[0]&0xF8)==0xF0 && (p_line[1]&0xC0)==0x80 && (p_line[2]&0xC0)==0x80 && (p_line[3]&0xC0)==0x80) len+=3;
         }
         ++len;
         ++n;
       }
       PyObject *ret = PyUnicode_Decode(p_line,len,pcio_enc,"replace");
       p_line+=len;
       return ret;
    }
    if(count_c>=0)
      ret=PyList_New(count_c);
    for(int i=0;i<count_c || count_c==-1;++i) {
      PyObject *obj;
      if(fmt_c==1)
        obj=input_1(fmt_mode);
      else
        obj=input_2(fmt_kind,fmt_len, fmt,fmt_c);
      if(count_c==-1)
         return obj;
      PyList_SET_ITEM(ret,i,obj);
    }
    return ret;
}
