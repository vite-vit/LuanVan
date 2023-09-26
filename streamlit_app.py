import streamlit as st
from streamlit_chat import message
import requests
import openai 
import pandas as pd
from configs import *
import json
import numpy as np
from PIL import Image, ImageDraw
import chromadb
from build_db import collection,client

col1,_ = st.columns([1,2])
with col1:
    logo_image = Image.open(f"{PATH_LOGO}/logo.jpeg")
    st.image(logo_image)

df = pd.read_parquet(PATH_CHUNKS)
meta_image = json.loads(open(PATH_METADATA).read())
#Query from database fuction
def get_content_from_query(question, collection, num_content=5):
    results = collection.query(
        query_texts=question,
        include=["documents"],
        n_results=num_content,
    )
    return list(zip(results['ids'][0], results['documents'][0]))
### Call API
def Call_API(promt):
    openai.api_key = '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'
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": promt}
        ],
        temperature=0
    )
    a = response.choices[0].message['content']
    return json.loads(a)
st.title("BKSI Chatbot")

with st.chat_message("assistant"):
    st.write("Chào bạn! Tôi là BKSI - Chatbot cung cấp các thông tin về trường Đại học Bách Khoa - Đại học Quốc gia Tp.HCM.Tương tác với tôi để đặt câu hỏi hoặc mô tả công việc bạn cần tôi giúp đỡ. Tôi sẵn sàng hỗ trợ bạn một cách tốt nhất có thể.")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

input_user = st.chat_input("Enter your question")
if input_user:
    with st.chat_message("user"):
        st.markdown(input_user)
    contents = [get_content_from_query(
        question=input_user,
        collection=collection
    )]

    # Define prommt
    promt_content = []
    for content in contents:
        c = f"""
            ID: {content[0]}
            Nội dung: {content[1]}
            """
        promt_content.append(c)

    string_content = "\n\n".join(promt_content)

    intro = "Bạn hãy đóng vai trò là một người tư vấn viên của Đại Học Bách Khoa HCM, Dựa vào thông tin được cung cấp hãy trả lời câu hỏi của người dùng sao cho xác nghĩa với câu hỏi nhất"
    question = f"Câu hỏi: {input_user}"
    action = """
    Từ câu hỏi các các nội dung được cung cấp hãy trả về nội theo cấu trúc json sau(tuyệt đối không được tự nghĩ ra câu trả lời nằm ngoài nội dung cung cấp):
    - Nếu ngôn ngữ ở question không phải là tiếng Việt thì trả lời là:
        {
        "id": "None"
        "answer":"Xin lỗi nhưng tôi chỉ hỗ trợ tiếng Việt"
        }
    - Nếu chuỗi kí tự ở question không có ý nghĩa thì trả về:
        {
        "id": "None"
        "answer":"Dường như bạn đã nhập một chuỗi ký tự không liên quan hoặc không có ý nghĩa. Nếu bạn có bất kỳ câu hỏi hoặc yêu cầu cụ thể nào, hãy gửi cho tôi để tôi có thể hỗ trợ bạn."
        }
    - Nếu không chắc chắn hay chuỗi kí tự được nêu ra ở questions không có ý là một câu hỏi thì phải trả về:
        {
        "id": "None"
        "answer":"Dường như bạn đã nhập "input_user" nhưng tôi không chắc chắn bạn đang tìm kiếm thông tin hoặc sự hỗ trợ gì cụ thể. Vui lòng cung cấp thêm ngữ cảnh hoặc làm rõ yêu cầu của bạn, và tôi sẽ cố gắng hỗ trợ bạn tốt nhất có thể."
        }
    - Nếu không tìm ra câu trả lời trong các nội dung đã cung cấp:
        {
            "id": "None",
            "answer": "Xin lỗi vì sự bất tiện này.Bạn có thể đặt câu hỏi khác được không ?" 
        }
        
    - Nếu tìm thấy câu trả lời:
        {
            "id": "chỉ được là ID của nội dung nào mà có câu trả lời, không được có nội dung của câu trả lời",
            "answer": "Câu trả lời được dựa vào nội dung cung cấp"
        }

    """

    PROMT = "\n".join([intro, question, string_content, action])
    
    st.session_state.messages.append({"role": "user","content": input_user})
    

    with st.chat_message("assistant"):
        response = Call_API(PROMT)
        st.markdown(response["answer"])
    st.session_state.messages.append({"role": "assistant","content": response["answer"]})
    ID = response["id"]
    print(response)
   
    if ID != "None":
        with st.expander("Hiển thị nội dung trích dẫn"):
            ### Visualize image 
            st.header("Trích từ tài liệu:")
            data = df[df['idx_chunk']==ID]
            idx_doc = data['idx_doc'].tolist()[0]
            chunk_meta = data['chunk_meta'].tolist()[0]
            meta_image[idx_doc]['pdf_path']
            path_images = meta_image[idx_doc]['pdf_images']
            visual = dict()
            for e in chunk_meta:
                if e['page'] not in visual:
                    visual[e['page']] = {
                        "path_image": path_images[e['page']],
                        "meta": None
                    }
                    visual[e['page']]['meta'] = [
                        {
                            'bbox': e['bbox'],
                            'word': e['word']
                        }
                    ]
                else:
                    visual[e['page']]['meta'].append(
                        {
                            'bbox': e['bbox'],
                            'word': e['word']
                        }
                    )
            all_ = list(visual.values())
            sample = all_[0]
            image = Image.open(sample['path_image'])
            meta = sample['meta']
            drawer = ImageDraw.Draw(image)
            for box_word in meta:
                bbox = list(box_word['bbox'])
                word = box_word['word']
                drawer.rectangle(bbox, outline='red',width=2)
            st.image(image, caption='Nguồn tài liệu')



