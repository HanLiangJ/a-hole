# a-hole

some handy demo

### ObjModefied.py
for .obj file modefied.  
用于.obj文件的3d模型的图像变换。

通过对点面的处理，完成脚型（.obj格式)的基础变换。
基础变换：模型平移，镜像变换，质心对齐，中心对齐等

### Log.py
customized undo/redo logger module.  
一个定制的操作记录模块。  

主要功能：  
1.undo/redo：可以对已完成的操作进行undo/redo操作。  
主要的实现方法是将对象保存在undo栈中，undo/redo操作时将其取出，利用空间换时间和算法实现复杂度  
2.工程模块：自定义了一个工程文件对象，提供了相关调用接口。
3.操作记录问价：提供了将操作命令的指令和参数进行保存/读取的操作，读取操作未完善成功，仅支持读操作，但读取后还未实现重现历史记录的功能。  