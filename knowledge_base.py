'''知识库'''
import os
import config_data as config
import hashlib #计算字符串的md5值
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter #递归文本分割器
from datetime import datetime
def check_md5(md5_str:str):
    '''检查传入的md5字符串是否已经被处理过了

    return False 表示没有处理过这个md5
    return True  表示处理过这个md5'''
    if not os.path.exists(config.md5_path):
        #if进入表示文件不存在，那肯定没有处理过这个md5了
        with open(config.md5_path,'w',encoding='utf-8') as f:
            pass
        return False
    with open(config.md5_path,'r',encoding='utf-8') as f:
        lines =[i.strip() for i in f.readlines()]
        return md5_str in lines



def save_md5(md5_str:str):
    '''将传入的md5字符串，记录到文件内保存'''
    with open(config.md5_path,'a',encoding='utf-8') as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str:str,encoding='utf-8'):
    '''将传入的字符串转换成md5字符串'''

    #将字符串转换成bytes字节数组，也就是还原成二进制
    str_bytes = input_str.encode(encoding = encoding)

    #创建md5对象
    md5_obj = hashlib.md5()  #得到md5对象
    md5_obj.update(str_bytes)#传入即将要转换的字节数组
    md5_hex = md5_obj.hexdigest()#得到md5的16进制字符串
    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        #如果文件夹不存在则创建。如果存在则跳过
        os.makedirs(config.persist_directory,exist_ok=True)
        self.chroma = Chroma(
            collection_name = config.collection_name, #数据库表名
            embedding_function = DashScopeEmbeddings(model = "text-embedding-v4"),#创建嵌入函数,把字符串转换成向量
            persist_directory = config.persist_directory #数据库本地存储文件夹
        )  #向量存储的实例 Chroma数据库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = config.chunk_size, #分割后的文本段最大长度
            chunk_overlap = config.chunk_overlap, #连续文本段之间的字符重叠数量
            separators = config.separators, #自然段落划分的分隔符
            length_function = len #使用Python的len函数来计算长度
        ) #文本分割器的对象

    def upload_by_str(self,data,filename):
        '''将传入的字符串，进行向量化，存入向量数据库中'''
        #先得到传入的字符串的md5值
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"

        if len(data) >config.max_split_char_number:
            knowledge_chunks=self.spliter.split_text(data) #文本分割
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小曹"
        } #数据的元信息

        self.chroma.add_texts( #内容就加载到向量数据库中了
            texts = knowledge_chunks,
            metadatas = [metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex) #将md5值记录到文件内保存

        return "[保存]内容已保存到知识库"


if __name__ == '__main__':
    service = KnowledgeBaseService()
    r =service.upload_by_str("周杰伦","testfile")
    print(r)