import fitz
from utils import normalize_box, unnorm_box
from fitz import Matrix
import io
from PIL import Image
import os
from configs import *

def is_inline(box1, box2, threshold=0.7):
    def overlap(start1, end1, start2, end2):
        s = abs(max(end2, end1) - min(start1, start2))
        return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)/s
    return overlap(box1[1], box1[3], box2[1], box2[3]) > threshold

def cluster_lines(boxes, threshold=0.7):
    # Sắp xếp các hộp theo tọa độ y
    boxes.sort(key=lambda x: x['bbox'][1])

    clusters = []
    current_cluster = [boxes[0]]

    for i in range(1, len(boxes)):
        if is_inline(current_cluster[0]['bbox'], boxes[i]['bbox'], threshold):
            # Nếu hộp nằm trên cùng một hàng, thêm vào cluster hiện tại
            current_cluster.append(boxes[i])
        else:
            # Nếu không, tạo một cluster mới và thêm hộp vào cluster mới
            current_cluster.sort(key=lambda x: x['bbox'][0])  # Sắp xếp các từ trong cluster theo tọa độ x
            clusters.append(current_cluster)
            current_cluster = [boxes[i]]

    # Thêm cluster cuối cùng
    clusters.append(current_cluster)
    clusters = sorted(clusters, key=lambda x: x[0]['bbox'][1])
    return clusters

def filter(bboxes, y_min=50, y_max=900):
    def condition(box, y_min=y_min, y_max=y_max):
        if box[1] > y_min and box[1] <y_max:
            return True
        else:
            return False
    return [box for box in bboxes if condition(box['bbox'])]


def join_words_into_lines(words_list):
    lines = {}
    for word_info in words_list:
        page = word_info['page']
        line = word_info['line']
        word = word_info['word']

        if (page, line) in lines:
            lines[(page, line)].append(word)
        else:
            lines[(page, line)] = [word]

    joined_lines = []
    for (page, line), words in sorted(lines.items()):
        joined_line = ' '.join(words)
        joined_lines.append(joined_line)

    return '\n'.join(joined_lines)

def split_into_chunks(data, chunk_size=256, stride=128):
    chunks = []
    i = 0
    idx = 0
    while i < len(data):
        if i + chunk_size <= len(data):
            chunk = data[i:i+chunk_size]
            temp = {
                'idx': idx,
                'chunk_meta': chunk,
                'chunk_content': join_words_into_lines(chunk)
            }
            chunks.append(temp)
            i += stride
        else:
            chunk = data[i:]
            temp = {
                'idx': idx,
                'chunk_meta': chunk,
                'chunk_content': join_words_into_lines(chunk)
            }
            chunks.append(temp)
            break
        idx+=1
    return chunks

def preprocess_docs(path, cfg):
    docs = fitz.open(path)
    pdf_bbox_word = []
    pdf_images = []
    pdf_name = path.split('/')[-1]
    for idx, page in enumerate(docs):
        page_bbox_word = []
        zoom = 3
        mat = Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes())) 
        path_save_image = os.path.join(FOLDER_IMAGES, f"{pdf_name[:-4]}_page_{idx}.png")
        img.save(path_save_image)
        w_origin, h_origin = img.size
        pdf_images.append(path_save_image)
        infors = page.get_text("words")
        w, h = page.mediabox[2:4]
        for infor in infors:
            word = infor[4]
            bbox = normalize_box(infor[:4], w, h)
            bbox = unnorm_box(bbox,w_origin, h_origin)
            page_bbox_word.append({
                'bbox':bbox,
                'word': word,
                'page': idx
            })

        pdf_bbox_word.append(page_bbox_word)
    pdf_bbox_word_filter = []
    for page_ in pdf_bbox_word:
        page_filter = filter(
            page_, 
            y_min=cfg['y_min'], 
            y_max=cfg['y_max']
        )
        if page_filter != []:
            cluster_bboxes = cluster_lines(page_filter)
            for line_idx, line in enumerate(cluster_bboxes):
                if line != []:
                    for element in line:
                        element['line'] = line_idx
                        pdf_bbox_word_filter.append(element)
    
    chunks = split_into_chunks(
            pdf_bbox_word_filter, 
            chunk_size = cfg['chunk_size'], 
            stride = cfg['chunk_stride']
        )
    return {
        "pdf_path": pdf_name,
        'pdf_images': pdf_images,
        "chunks": chunks
    }

def indexing_documents(docs):
    meta_doc = dict()
    chunks = []
    count = 0
    for idx,doc in enumerate(docs):
        meta_doc[f'doc_{idx}'] = {
            'pdf_path': doc['pdf_path'],
            'pdf_images': doc['pdf_images'],
        }
        doc['chunks'] = sorted(doc['chunks'], key=lambda x:x['idx'])
        for chunk in doc['chunks']:
            chunk_new = dict()
            chunk_new['idx_chunk']= f"chunk_{count}"
            chunk_new['idx_doc'] = f"doc_{idx}"
            chunk_new['chunk_meta'] = chunk['chunk_meta']
            chunk_new['chunk_content'] = chunk['chunk_content']
            chunks.append(chunk_new)
            count +=1
    return chunks, meta_doc