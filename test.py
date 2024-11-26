

# import os
# from flask import Flask, request, render_template
# from google_img_source_search import ReverseImageSearcher
# from pymongo import MongoClient
# import time

# app = Flask(__name__)

# # Cấu hình MongoDB
# MONGODB_URI = 'mongodb+srv://khanhduc2902:khanhduc2902@cluster0.03at6jt.mongodb.net/cuahangdientu'
# client = MongoClient(MONGODB_URI)
# db = client['cuahangdientu']
# product_collection = db['products']

# # Danh sách các từ khóa chính liên quan đến thương hiệu và sản phẩm
# KEYWORDS = ["Sony", "Samsung", "iPhone", "Oppo", "Nokia", "Huawei", "Vivo", "HTC", "LG", "LENOVO", "HUAWEI", "ASUS", "APPLE", "ASUS"]

# def setUp():
#     return ReverseImageSearcher()

# def extract_main_keywords(title):
#     stopwords = ["support", "for", "dịch vụ", "công nghệ", "hỗ trợ", "trang"]
#     words = title.split()
#     filtered_words = [word for word in words if word not in stopwords and (word in KEYWORDS or word.isalnum())]
#     keyword = " ".join([word for word in filtered_words if word in KEYWORDS] or filtered_words[:2])
#     return keyword

# def find_product_by_image_url(image_url):
#     rev_img_searcher = setUp()
#     results = rev_img_searcher.search(image_url)

#     if not results:
#         return None, "Không tìm thấy hình ảnh tương tự."

#     closest_match_title = results[0].page_title
#     keyword = extract_main_keywords(closest_match_title)
#     query = {"title": {"$regex": keyword, "$options": "i"}}
#     matched_products = list(product_collection.find(query))

#     if not matched_products:
#         return None, "Không tìm thấy sản phẩm nào trong cơ sở dữ liệu."

#     return matched_products, None

# def find_product_by_image_file(file_path):
#     reverse_image_searcher = setUp()
    
#     # Truyền đường dẫn tệp thay vì đối tượng tệp
#     results = reverse_image_searcher.search_by_file(file_path)
    
#     if not results:
#         return None, "Không tìm thấy hình ảnh tương tự."

#     closest_match_title = results[0].page_title
#     keyword = extract_main_keywords(closest_match_title)
#     query = {"title": {"$regex": keyword, "$options": "i"}}
#     matched_products = list(product_collection.find(query))

#     if not matched_products:
#         return None, "Không tìm thấy sản phẩm nào trong cơ sở dữ liệu."

#     return matched_products, None

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/search', methods=['POST'])
# def search():
#     image_url = request.form.get('image_url')
#     uploaded_file = request.files.get('image_file')

#     if image_url:
#         matched_products, error_message = find_product_by_image_url(image_url)
#     elif uploaded_file:
#         # Lưu tệp hình ảnh tải lên vào thư mục IMG-Search
#         img_search_path = r'D:\Do_An_Tot_Nghiep\Be\Google-Reverse-Image-Search\uploads'
#         file_path = os.path.join(img_search_path, uploaded_file.filename)
#         uploaded_file.save(file_path)

#         matched_products, error_message = find_product_by_image_file(file_path)

#         # Tùy chọn: xóa tệp sau khi xử lý
#         os.remove(file_path)  # Dọn dẹp sau khi xử lý
#     else:
#         return render_template('index.html', error="Vui lòng cung cấp URL hình ảnh hoặc tải lên hình ảnh.")

#     if error_message:
#         return render_template('index.html', error=error_message, image_url=image_url)

#     return render_template('index.html', products=matched_products, image_url=image_url)



# if __name__ == '__main__':
#     # Đảm bảo thư mục uploads tồn tại
#     os.makedirs('uploads', exist_ok=True)
#     app.run(debug=True)




#

from flask import Flask, request, jsonify
from google_img_source_search import ReverseImageSearcher
from pymongo import MongoClient
from flask_cors import CORS
import os
from bson import ObjectId  # Import ObjectId từ bson

app = Flask(__name__)
CORS(app)

MONGODB_URI = 'mongodb+srv://khanhduc2902:khanhduc2902@cluster0.03at6jt.mongodb.net/cuahangdientu'
client = MongoClient(MONGODB_URI)
db = client['cuahangdientu']
product_collection = db['products']

KEYWORDS = ["Sony", "Samsung", "iPhone", "Oppo", "Nokia", "Huawei", "Vivo", "HTC", "LG", "LENOVO", "HUAWEI", "ASUS", "APPLE", "ASUS"]

def setUp():
    return ReverseImageSearcher()

def extract_main_keywords(title):
    stopwords = ["support", "for", "dịch vụ", "công nghệ", "hỗ trợ", "trang"]
    words = title.split()
    filtered_words = [word for word in words if word not in stopwords and (word in KEYWORDS or word.isalnum())]
    keyword = " ".join([word for word in filtered_words if word in KEYWORDS] or filtered_words[:2])
    return keyword

# def serialize_product(product):
#     """Chuyển đổi đối tượng sản phẩm thành kiểu JSON."""
#     product['_id'] = str(product['_id'])  # Chuyển ObjectId thành chuỗi
#     return product
def serialize_product(product):
    """Chuyển đổi tất cả ObjectId trong đối tượng sản phẩm thành chuỗi để tương thích với JSON."""
    if isinstance(product, dict):
        for key, value in product.items():
            if isinstance(value, ObjectId):
                product[key] = str(value)
            elif isinstance(value, dict):  # Nếu là từ điển lồng nhau, gọi đệ quy
                product[key] = serialize_product(value)
            elif isinstance(value, list):  # Nếu là danh sách, xử lý từng phần tử
                product[key] = [serialize_product(v) if isinstance(v, dict) else str(v) if isinstance(v, ObjectId) else v for v in value]
    return product

def find_product_by_image_url(image_url):
   
    rev_img_searcher = setUp()
    results = rev_img_searcher.search(image_url)

    if not results:
        return None, "Không tìm thấy hình ảnh tương tự."

    closest_match_title = results[0].page_title
    keyword = extract_main_keywords(closest_match_title)
    query = {"title": {"$regex": keyword, "$options": "i"}}
    matched_products = list(product_collection.find(query))

    if not matched_products:
        return None, "Không tìm thấy sản phẩm nào trong cơ sở dữ liệu."

    return matched_products, None

def find_product_by_image_file(file_path):
    reverse_image_searcher = setUp()
    results = reverse_image_searcher.search_by_file(file_path)

    if not results:
        return None, "Không tìm thấy hình ảnh tương tự."

    closest_match_title = results[0].page_title
    keyword = extract_main_keywords(closest_match_title)
    query = {"title": {"$regex": keyword, "$options": "i"}}
    matched_products = list(product_collection.find(query))

    if not matched_products:
        return None, "Không tìm thấy sản phẩm nào trong cơ sở dữ liệu."

    return matched_products, None

@app.route('/search', methods=['POST'])
def search():
    # In ra loại dữ liệu được gửi từ client
    print("Content-Type:", request.content_type)  
    
    # Lấy image_url từ request.form
    image_url = request.form.get('image_url')
    uploaded_file = request.files.get('image_file')

    if image_url:
        matched_products, error_message = find_product_by_image_url(image_url)
    elif uploaded_file:
        # img_search_path = r'D:\Do_An_Tot_Nghiep\Shop_HB-master\Shop\img-search-server\uploads'

        base_path = os.path.dirname(__file__)  # Đường dẫn thư mục chứa file hiện tại
        img_search_path = os.path.join(base_path, 'uploads')

        if not os.path.exists(img_search_path):
            os.makedirs(img_search_path)  # Tạo thư mục nếu chưa tồn tại
        

        file_path = os.path.join(img_search_path, uploaded_file.filename)
        uploaded_file.save(file_path)
        matched_products, error_message = find_product_by_image_file(file_path)
        os.remove(file_path)
    else:
        return jsonify({"error": "Vui lòng cung cấp URL hình ảnh hoặc tải lên hình ảnh."}), 400

    if error_message:
        return jsonify({"error": error_message}), 404

    # Chuyển đổi tất cả sản phẩm sang dạng JSON
    serialized_products = [serialize_product(product) for product in matched_products]
    
    return jsonify({"products": serialized_products})

if __name__ == '__main__':
    # os.makedirs('uploads', exist_ok=True)  # Bỏ comment nếu cần tạo thư mục uploads
    app.run(debug=True)

