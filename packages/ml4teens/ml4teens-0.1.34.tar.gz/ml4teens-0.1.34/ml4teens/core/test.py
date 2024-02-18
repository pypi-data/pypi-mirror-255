import random;
import string;
import threading;
import time;
import queue;

#===============================================================================      
class Parameters:
      
      def __init__(self, args):
          super().__setattr__('_data',  dict());                
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__init__", flush=True);
          for key in args:
              data[key]=args[key];
          
      def __setitem__(self, key, value):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__setitem__", flush=True);
          if value is not None: data[key]=value;
          else:                 self.__delitem__(key);

      def __getitem__(self, key):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__getitem__", flush=True);
          return data[key];

      def __delitem__(self, key):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__delitem__", flush=True);
          if key in data: del data[key];
          
      def __iter__(self):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__iter__", flush=True);
          return iter(data);

      def __len__(self):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__len__", flush=True);
          return len(data);

      def __contains__(self, key):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__contains__", flush=True);
          return (key in data) and (data[key] is not None);
          
      def __getattr__(self, key):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print(f"__getattr__('{key}')", flush=True);
          if key=="keys":   return data.keys;
          if key=="items":  return data.items;
          if key=="values": return data.values;
          if key=="update": return data.update;
          if key=="pop":    return data.pop;
          if key=="clear":  return data.clear;
          return data.get(key,None);

      def __setattr__(self, key, value):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("__setattr__", flush=True);
          if value is not None: data[key]=value;
          else:                 del data[key];

      def get(self, key, default=None):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("get()", flush=True);
          return data.get(key,default);
          
      def exists(self, key, types=None):
          data=self.__dict__.get('_data',None);
          assert data is not None;
          print("exists()", flush=True);
          return (key in data) and (types is None or any([isinstance(data[key],tp) for tp in types]));
      
if __name__=="__main__":
   
   params=Parameters(args={"1":1, "2":2, "3":3});
   
   print({**params});
   