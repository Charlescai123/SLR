import os
from FileUtils.WorkSpace import WorkSpace
from FileUtils.ZFile import ZFile
from DevisignUtils.RecordSource import RecordSource
from Convertor.StreamController import StreamController


# 示例 
#from Convertor.Exactor.TestExactor import RoundExactor as Exactor
# 深度、肤色、骨骼综合 算法
from Convertor.Extractor.MixedExtractor import MixedExtractor as Extractor

class genTrainDataFromZipFile(object):
    def __init__(self, target_ws, extract_func, tmp_folder='tmp_video_folder'):
        self.tmp_ws = WorkSpace('Tmp', tmp_folder)
        self.target_ws = target_ws
        
        # 如何把原视频转为
        self.extract_func = extract_func

        # 清空原先数据库
        self.target_ws.deleteFolder(remove_non_empty=True)
        # 重新生成索引记录文件
        self.index_file = open(self.target_ws.touch('index'), 'w')
        self.counter = 0

    def handleSingleTrainData(self, zip_file_path):
        self.counter += 1
        print('Now handling {}.th Data '.format(self.counter))

        # 将一个 zip 文件解压到临时文件夹
        zip_file = ZFile(zip_file_path)
        zip_file.extract_to(self.tmp_ws.path)

        name = self.tmp_ws.getFolderStructure('.')[0]
        label_name = int(name.split('_')[-4])
        filename = name.split('\\')[1].split('.')[0]        # 去.oni后缀之后的文件名
        # print("filename is *****************"+filename)
        # print("name is****************************"+name)
        # print("label name is:************"+str(label_name))

        # 确定有相关标签的文件夹

        # self.target_ws.checkPath('{:03d}'.format(label_name))

        # 通过标记计算是该标签下的第几个样本
        #target_file = self.target_ws.countinueNaming(os.path.join('{:03d}'.format(label_name), '{}'), isFloder=False)
        #target_file =
        target_file = self.target_ws.countinueNaming(os.path.join(filename,),isFloder=False)

        print("target_file is************3131312312312312*****************"+target_file)
        #open(target_file, 'wb').close()

        # 读入源数据
        source = RecordSource(name)

        # !!!!!!!!!!!!!!!! 注意  !!!!!!!!!!!!!!!!!!!!!!!
        # 此时 输入为 : source , 指定输出文件的前缀为 : target_file (.npy)
        self.extract_func(source, target_file)

        # 添加至索引
        self.index_file.write('{:03d} {}\n'.format(label_name, target_file+'.npy'))
        self.index_file.flush()

        # 移除临时文件
        self.tmp_ws.deleteFolder(remove_non_empty=True)

    def cleanUp(self):
        self.tmp_ws.deleteWS()




if __name__ == "__main__":

    def exact_func(source,target_file):
        pass

    filepath="./Data/DEVISIGN_D/"
    # 源数据库 路径
    source_folder_path = filepath
    # 目标数据库 路径
    target_folder_path = 'video_out'

    # 源路径 : DEVISIGN 数据库 : 不要解压里面的 .zip 文件 !!! 解压 RAR 文件就够了!
    source_ws = WorkSpace('Source', source_folder_path)
    # 目的路径 : 提取出的数据存放位置
    target_ws = WorkSpace('Target', target_folder_path)

    # 提取算法 exactor.exact
    extractor = Extractor()

    # 视频流转化控制器 stack_size 描述从视频中抽出多少帧形成训练数据，target_size 描述转化后的帧需要压缩到什么尺寸以减少数据量
    streamController = StreamController(extractor.extract, stack_size=24, target_size=None)

    generator = genTrainDataFromZipFile(target_ws=target_ws, exact_func=streamController.Convert)
    source_ws.applyFunctionTo(generator.handleSingleTrainData, depth=2)

    generator.cleanUp()



