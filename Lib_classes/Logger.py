import os
import sys
from pprint import pprint
from typing import Any, Optional, Type

from tqdm import tqdm


class LoggerEmpty:
    def __init__(self, name:str|None = '?'):
        self.name = name
        
    def __call__(self, obj:Any):
        pass
            
            
    def presbar1(self, obj:Any):
        pass
    
    def presbar(self, name:str|None, len:int):
        
        class Brogressbar:
            def __init__(self, len:int|None, name:str|None):
                pass
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            def __call__(self, i:int = 1, label:str|None = None):
                pass
                
                

        return Brogressbar(len, self.name)
    
    def make_child(self, add_str: str, type: type["LoggerEmpty"] | None = None):
        if type is not None:
            return type(f'{self.name}\\{add_str}')
        else:
            return self.__class__(f'{self.name}\\{add_str}')
    

    def error(self, obj:Any, type_error:type[BaseException] | None = None):
        if type_error is not None:
            raise type_error(obj)
        
        if isinstance(obj, BaseException):
            raise obj
        else:
            raise Exception(obj)
        

    
class Logger(LoggerEmpty):
    def __init__(self, name:str|None = None):
        if sys.platform == 'win32':
            from colorama import just_fix_windows_console
            just_fix_windows_console()
        if name is None:
            self.name = '?'
        else:
            self.name = name
        
        
    def __call__(self, obj:Any):
        if isinstance(obj, str):
            print(f'{self.name}: {obj}')
        else:
            print(f'{self.name}:', end='')
            pprint(obj)
    
    def presbar(self, name:str|None, len:int):
        if name is None:
            name = self.name
        else:
            name = os.path.join(self.name,  name)
            
        class Brogressbar:
            def __init__(self, length: int, name: str):
                self.len = length
                self.name = name

            def __enter__(self):
                self.bar = tqdm(total=self.len, desc=self.name, leave=True)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.bar.close()

            def __call__(self, i: int = 1, label: str | None = None):
                self.bar.update(i)
                if label:
                    self.bar.set_postfix_str(label)
                    
        return Brogressbar(len, name)