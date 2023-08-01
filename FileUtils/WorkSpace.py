# encoding: utf-8
# author: daijianbang

import os,sys
import shutil


class WorkSpace(object):
    def __init__(self, ws_name, ws_path):    # 初始化
        self.name = ws_name
        self.path = ws_path
        print('Workspace : {}  at Dir : {}'.format(self.name, self.path))
        self.checkPath()

    def getFolderStructure(self, path):  # 获取文件夹下所有文件的路径
        path = os.path.join(self.path, path)

        assert os.path.exists(path) 
        assert os.path.isdir(path)
 
        _paths = os.listdir(path)
        paths = []
        for path in _paths:
            paths.append(os.path.join(self.path, path))
        return paths

    def checkPath(self, path='.'):   # 检查路径是否存在
        path = self.getRelativePath(path)

        if not os.path.exists(path):
            print("Workspace {} @ {} : create new : {}".format(self.name, self.path, path))
            os.makedirs(path)
        else:
            assert not os.path.isfile(path)
    
    def touch(self, path, subfix='.txt'):     # 获取相关.txt文件的路径
        path = os.path.join(self.path, path)
        path = path+subfix

        assert not os.path.exists(path)
        f = open(path, 'wb')
        f.close()
        return path

    def getRelativePath(self, path):  # 获取相关路径
        return os.path.join(self.path, path)

    def applyFunctionTo(self, functions, path='.', depth=0):
        base_path = self.getRelativePath(path)  # 基路径
        tmp_path = base_path

        def applyFunc(functions,tmp_path):
            if isinstance(functions, list):  # 检测是不是列表
                for func in functions:
                    func(tmp_path)
            else:
                functions(tmp_path)

        if not depth:
            applyFunc(functions, tmp_path)

        else:
            # tree data struct 树形数据结构访问
            def visit(tmp_path=base_path, curr_depth=0, target_depth=depth):
                counter = 0
                if curr_depth == target_depth:
                    applyFunc(functions, tmp_path)
                    return 1
                else:
                    paths = os.listdir(tmp_path)
                    for path in paths:
                        counter += visit(os.path.join(tmp_path, path), curr_depth+1, target_depth)
                    return counter
            
            times = visit()  # 访问次数
            print("Workspace {} report : Apply {} times".format(self.name, times))

    def deleteFolder(self, path='', remove_non_empty=False):      # 删除文件夹
        path = self.getRelativePath(path)
        if not os.path.exists(path):
            return
        if not remove_non_empty:
            os.removedirs(path)
        else:
            shutil.rmtree(path)   
        self.checkPath()

    def deleteWS(self):         # 删除工作空间
        shutil.rmtree(self.path)
        print("Workspace {} report : WS removed".format(self.name))

    def countinueNaming(self, name='{}', path='.', isFloder=True, beginFrom=0):     # 对一个工作目录下所有文件命名
        name = self.getRelativePath(name)
        tmp_name = name.format(beginFrom)
        if isFloder:
            while os.path.exists(tmp_name) and os.path.isdir(tmp_name):
                beginFrom += 1
                tmp_name = name.format(beginFrom)
            os.makedirs(tmp_name)
        else:
            while os.path.exists(tmp_name) and not os.path.isfile(tmp_name):
                beginFrom += 1
                tmp_name = name.format(beginFrom)
            return tmp_name


if __name__ == "__main__":
    source_ws = WorkSpace('Source', 'E:/ProjectBackup/HandPy/DEVISIGN_G/')
    def printfunc(foldername):
       # file_names=os.listdir(foldername)
       # for file_name in file_names:
        print(foldername)
    source_ws.applyFunctionTo(printfunc, depth=2)
    
    target_ws = WorkSpace('Tmp', 'tmp_path')

    for i in range(10):
        target_ws.countinueNaming('label_{}.txt', isFloder=False)
   # target_ws.deleteFolder(remove_non_empty=True)



