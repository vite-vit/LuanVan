## BSKI chatbot
### Python 
sudo apt update && sudo apt install python3-dev python3.10-venv build-essential -y
python3 -m venv .venv
source .venv/bin/activate

1. Environment:
- Yêu cầu python 3.10
- Tải về các thư viện cần thiết
    -  ```pip install -r requirements.txt```
2. Xử lý data:
-  Khi chạy lần đầu hoặc thay đổi data thì xoá những file trong thư mục database/image và database/meta database/vector
- Sau đó chạy file chunk.py
    - ``` python chunk.py ```
3. Chạy streamlit app:
    - ```streamlit run streamlit_app.py```