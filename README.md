# a-hole

    some handy demo.
### ObjModefied.py
for .obj file modefied.  
用于.obj文件的3d模型的图像变换。

    主要功能：通过对点面的处理，完成脚型（.obj格式)的基础变换。  
    基础变换：平移，镜像翻转，质心对齐，中心对齐等。
    主要算法：3d模型质心计算的python实现
***

### Log.py
customized undo/redo logger module.  
一个定制的操作记录模块。  

主要功能：  

    1.undo/redo：可以对已完成的操作进行undo/redo操作。  
        实现方法：将对象的拷贝保存在undo栈中，undo/redo操作时将其取出，利用空间换时间和算法实现复杂度。  
        其他可实现方法：将每个操作方法添加undo和redo方法，但代码量庞大，而且对于复杂操作指令会需要将其复杂的undo/redo改写。  
    2.工程模块：自定义了一个工程文件对象，提供了相关调用接口。  
        实现方法：通过json文件保存相关文件的相对路径，load时将相对路径改为绝对路径，save时将相对路径改为绝对路径保存。
    3.操作记录：提供了将操作命令的指令和参数进行保存/读取的操作。   
        存在问题：读取操作未完善成功，仅支持读操作，但读取后还未实现重现历史记录的功能。
***

### LogMaker.py

a logger module using Singleton.

一个使用单例模式的日志记录模块

主要功能：

```
1.以日志记录形式输出到控制台/日志文件;
2.记录异常信息：如LogMaker.info("this is info:",5);
3.确认异常信息:LogMaker.check_error(condition,message,level);
```

