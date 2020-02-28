import copy
import os
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from collections import OrderedDict
import json


class Logger(pg.LayoutWidget):
    def __init__(self):
        '''【操作记录】管理器'''
        super().__init__()
        self.__initUI__()

        # 创建一个list存放当前UI展示的对象
        # 创建undo和redo栈
        self.record_name = None  # 操作记录文件名
        self.current_obj = []
        self.undostack = []  # (cmd_name,tree_item,last_obj)
        self.redostack = []

        self.opts = {}
        self.para = None
        # 工程管理器（用于工程的创建、保存、导入）
        self.project = Project()

        # 计数器，暂时无用
        self.cnt = 0

        self.trim_foot_param = {
            0: '前',
            1: '后',
            2: '上',
            3: '下',
            4: '左',
            5: '右',
        }

        self.opts = {
            'turn_foot': ['脚型反转', '对称变换'],
            'trim_foot': ['脚型位置调整', None],
            'stamp': ['脚楦匹配', '底面贴合']
        }

    def __initUI__(self):
        '''界面布局'''
        self.area = DockArea()
        self.addWidget((self.area))
        self.cmddock = Dock("操作记录", size=(2, 3))
        self.area.addDock(self.cmddock, "left")

        self.cmdlist = pg.TreeWidget()
        # self.cmdlist.setColumnCount(1)
        self.cmdlist.setHeaderLabel('操作记录')
        self.cmdlist.setColumnCount(2)
        self.cmdlist.setHeaderLabels(['操作记录', '调整参数'])
        self.cmdlist.setColumnWidth(0, 200)
        self.cmdlist.setColumnWidth(0, 150)
        self.cmdlist.setDragEnabled(False)
        self.cmdlist.setAcceptDrops(False)
        self.cmddock.addWidget(self.cmdlist)

        self.resize(400, 300)



    def createProject(self, file_dirname):
        # self.record_name=file_name+'/record.txt'
        self.project.create(file_dirname)

    def loadProject(self, file_path):
        self.project.load(file_path)
        self.loadhistory(self.project.recordFile)

    def saveProject(self, save_path, foot_name=None, last_name=None):
        # record_name = '/Operation.txt'
        # self.savehistory(dir_name + record_name)
        self.project.save(save_path, foot_name=foot_name, last_name=last_name, record_name=self.record_name)
        self.savehistory(self.project.recordFile)

    def loadhistory(self, file_name):
        '''
        载入历史记录
        :param file_name: 指定导入的文件名称
        '''

        # 清除现有操作记录
        self.clear()
        # 读取指定名称的操作记录文件至【操作记录】的UI界面
        self.record_name = file_name
        with open(file_name, 'r') as f:
            for cmd_line in f.readlines():
                cmd_line = cmd_line.strip('\n')
                cmd=cmd_line.split(' ')
                cmd_name=cmd[0]
                commanditem = pg.TreeWidgetItem([cmd[1],cmd[2]])
                self.cmdlist.addTopLevelItem(commanditem)
        # 更新界面
        self.update()

    def savehistory(self, file_path):
        '''
        保存操作记录
        :param file_name: 指定保存的文件名称
        '''
        # 将操作记录写入指定名称的文件中
        with open(file_path, 'w') as f:
            for cmd in self.undostack:
                f.write(cmd[0]+' '+cmd[1].text(0)+' '+cmd[1].text(1) + '（历史记录）\n')

    def undo(self):
        '''
        undo操作：
        1.undo栈pop：操作名，操作记录
        2.redo栈push：操作名，操作记录，当前对象
        3.undo栈pop：上一次操作对象；当前对象变为上一次操作对象
        4.【操作记录】管理器删除：已undo的操作记录
        '''

        # 判断undo栈是否存在过往操作记录，若没有则无法undo
        if self.undostack:
            # 1.undo栈pop：操作名和操作记录
            cmd_name = self.undostack[-1][0]
            commanditem = self.undostack[-1][1]
            # 2.redo栈push：【操作名，操作记录，当前对象】
            self.redostack.append((cmd_name, commanditem, self.current_obj))
            # 3.undo栈pop：上一次操作对象；当前对象变为上一次操作对象
            self.current_obj = self.undostack[-1][2]
            # 4.【操作记录】管理器删除：已undo的操作记录
            self.cmdlist.removeTopLevelItem(commanditem)
            self.undostack.pop()
        else:
            print("nothing to undo")

    def redo(self):
        '''
        redo操作：
        1.redo栈pop：操作名，操作记录
        2.undo栈push：操作名，操作记录，当前对象
        3.redo栈pop：上一次操作对象；当前对象变为上一次操作对象
        4.【操作记录】管理器恢复：已redo的操作记录
        '''

        # 判断redo栈是否存在已undo的过往操作记录，若没有则无法redo
        if self.redostack:
            # 1.redo栈pop：操作名，操作记录
            cmd_name = self.redostack[-1][0]
            commanditem = self.redostack[-1][1]
            # 2.undo栈push：操作名，操作记录，当前对象
            self.undostack.append((cmd_name, commanditem, self.current_obj))
            # 3.redo栈pop：上一次操作对象；当前对象变为上一次操作对象
            self.current_obj = self.redostack[-1][2]
            # 4.【操作记录】管理器恢复：已redo的操作记录
            self.cmdlist.addTopLevelItem(commanditem)
            self.redostack.pop()
        else:
            print("nothing to redo")

    def execute(self, cmd_name, foot_v, last_v, param=None):
        '''
        执行操作：
        1.判断redo栈是否存在操作记录，若有则删除
        2.拷贝被执行对象（不可直接用=赋值，这样执行前后的对象会指向同一地址）
        3.undo栈push：[执行操作名,操作记录,被执行对象]
        4.【操作记录】管理器UI添加操作记录
        :param cmd_name: 执行的操作记录名称
        :param obj: 被执行操作的对象（被执行对象）
        '''
        if self.redostack:
            self.redostack.clear()
        if cmd_name == 'trim_foot':
            self.opts[cmd_name][1] = '向{}平移{:.2f}mm'.format(self.trim_foot_param[param[0]], param[1])
        f = copy.copy(foot_v)
        l = copy.copy(last_v)
        last_obj = [f, l]  # 可改进
        commanditem = pg.TreeWidgetItem([self.opts[cmd_name][0],self.opts[cmd_name][1]])
        self.undostack.append((cmd_name, commanditem, last_obj))
        self.cmdlist.addTopLevelItem(commanditem)

    def get_current_foot(self):
        '''
        undo和redo操作后，getundo/redo后的当前脚型对象
        :return: getundo/redo后的当前脚型对象
        '''
        return self.current_obj[0]

    def get_current_shoe(self):
        '''
        undo和redo操作后，getundo/redo后的当前鞋楦对象
        :return: getundo/redo后的当前鞋楦对象
        '''
        return self.current_obj[1]

    def set_current_obj(self, foot_v, last_v):
        '''
        每次执行操作，获取要当前对象，存放于list中
        :param foot: 当前脚型对象
        :param last: 当前鞋楦对象
        '''
        self.current_obj = [copy.deepcopy(foot_v), copy.deepcopy(last_v)]

    def get_current_obj(self):
        return self.current_obj[0], self.current_obj[1]

    def clear(self):
        '''
        清空管理器的历史记录
        '''
        self.current_obj = []
        self.undostack = []
        self.redostack = []
        self.cmdlist.clear()
        # self.project.initPara()
        self.cnt = 0


class Project(object):
    def __init__(self):
        super(Project).__init__()
        # 用于外部类读写的参数
        self.projectFile = None  # 工程文件的绝对路径，不写入工程文件
        self.dir_name = None  # 工程文件所在目录的绝对路径目录，不写入工程文件
        self.lastFile = None  # 鞋楦所在的绝对路径，外部读取时的绝对路径，不写入工程文件
        self.footFile = None  # 脚型对象所在的绝对路径，不写入工程文件
        self.recordFile = None  # 操作记录文件所在的绝对路径，不写入工程文件

        # 用于写入工程文件的参数
        self.project = OrderedDict()  # 工程主文件，保存为json格式
        self.pDate = None  # 工程修改日期，写入工程文件
        self.projectName = None  # 工程文件名，写入工程文件
        self.foot_name = None  # 脚型对象的相对路径，写入工程文件
        self.last_name = None  # 鞋楦对象的相对路径，写入工程文件
        self.record_name = None  # 操作记录文件对象的相对路径，写入工程文件

    def initPara(self):
        pass

    def loadPara(self, dir_name):
        '''
        加载工程相关参数
        :return:
        '''
        # with open(self.projectFile,'')
        self.projectName = self.project['PROJECT_NAME']
        self.pDate = self.project['PROJECT_DATE']
        self.last_name = self.project['LAST_NAME']
        self.foot_name = self.project['FOOT_NAME']
        self.record_name = self.project['RECORD_NAME']

        self.lastFile = dir_name + self.last_name
        self.footFile = dir_name + self.foot_name
        self.recordFile = dir_name + self.record_name

    def writePara(self):
        import time
        self.project['PROJECT_NAME'] = self.projectName
        self.project['PROJECT_DATE'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.project['FOOT_NAME'] = self.foot_name
        self.project['LAST_NAME'] = self.last_name
        self.project['RECORD_NAME'] = self.record_name

        with open(self.projectFile, 'w') as file:
            json.dump(self.project, file, indent=4, separators=(',', ':'))

    def create(self, dir_name):
        self.dir_name = dir_name
        self.projectName = dir_name.split('/')[-1] + '.json'
        self.projectFile = dir_name + '/' + self.projectName

        self.writePara()

    def save(self, file_path, foot_name=None, last_name=None, record_name=None):
        '''
        保存project的名字
        foot,last,record的绝对地址->相对地址
        '''
        self.projectFile = file_path
        self.projectName = os.path.basename(file_path)
        self.dir_name = os.path.dirname(file_path)
        if foot_name and os.path.exists(foot_name):
            self.foot_name = '/' + os.path.basename(foot_name)
            self.footFile = self.dir_name + self.foot_name
        else:
            raise ValueError('不存在脚型文件')
        if last_name and os.path.exists(last_name):
            self.last_name = '/' + os.path.basename(last_name)
            self.lastFile = self.dir_name + self.last_name
        else:
            raise ValueError('不存在鞋楦文件')
        if record_name and os.path.exists(record_name):
            self.record_name = '/' + os.path.basename(record_name)
            self.recordFile = self.dir_name + self.record_name
        else:
            raise ValueError('不存在操作记录文件')
        self.writePara()

    def load(self, pName):
        if pName is not None and os.path.isfile(pName):
            self.projectFile = pName
            self.dir_name = os.path.dirname(self.projectFile)
            with open(pName, 'r') as file:
                self.project = OrderedDict(json.load(file))
                self.loadPara(self.dir_name)
        else:
            raise ValueError('请新建或导入工程文件')

# #test
# project=Project()
# project.write()
# project.save()
# project.load('../projectTest/test.json')
# foot_test=trimesh.load_mesh(project._footFile)
# print(foot_test.vertices)
