'''知识库更新主程序(streamlit)
基于streamlit完成WEB网页上传服务'''

import time
import streamlit as st
from knowledge_base import KnowledgeBaseService

#添加网页标题
st.title("知识库更新服务")

#file_uploader
uploader_file = st.file_uploader(
    "请上传TXT文件",  #提示词
    type="txt",           #文件类型
    accept_multiple_files = False,  #False表示仅接受一个文件的上传

)

#session_state就是一个字典,是一个消息容器
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader_file is not None:
    #提取文件的信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size  = uploader_file.size / 1024  #单位KB

    st.subheader(f"文件名:{file_name}")   #子标题
    st.write(f"格式:{file_type} | 大小:{file_size:.2f}KB")  #正常大小文字

    #get_value获取文件内容 ->bytes ->decode('utf-8')变成字符串
    text = uploader_file.getvalue().decode("utf-8")

    with st.spinner("载入知识库中......") :#在spinner内的代码执行过程中,会有一个转圈动画
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(text,file_name)
        st.write(result)


