## BSKI chatbot
### Python 
1. Environment:
- Yêu cầu python 3.10
- Tải về anaconda:
    -  ```pip install anaconda ```
- Tải về các thư viện cần thiết
    -  ```pip install -r requirements.txt```
2. Xử lý data:
-  Khi chạy lần đầu hoặc thay đổi data thì xoá những file trong thư mục database/image và database/meta database/vector
- Sau đó chạy file chunk.py
    - ``` python chunk.py ```
3. Chạy streamlit app:
    - ```streamlit run streamlit_app.py```