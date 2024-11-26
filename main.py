# from google_img_source_search import ReverseImageSearcher


# if __name__ == '__main__':
#     image_url = 'https://res.cloudinary.com/dqbnxvsrr/image/upload/v1729782847/cuahang-hb/omjh79flrgy4mmglqfws.jpg'

#     rev_img_searcher = ReverseImageSearcher()
#     res = rev_img_searcher.search(image_url)

#     print(len(res))

#     for search_item in res:
#         print(f'Title: {search_item.page_title}')
#         print(f'Site: {search_item.page_url}')
#         print(f'Img: {search_item.image_url}\n')


# import json
# import difflib
# from google_img_source_search import ReverseImageSearcher
# from pymongo import MongoClient


# MONGODB_URI = 'mongodb+srv://khanhduc2902:khanhduc2902@cluster0.03at6jt.mongodb.net/cuahangdientu'
# client = MongoClient(MONGODB_URI)
# db = client['cuahangdientu']
# product_collection = db['product']

# # Load the data.json file
# def load_data(file_path):
#     # with open(file_path, 'r', encoding='utf-8') as file:
#     #     data = json.load(file)
#     # return data
#     data = list(product_collection.find({}, {'_id': 0, 'name': 1}))  # only get 'name' field without '_id'
#     return data

# # Compare search result titles with product names using fuzzy matching
# def compare_and_print_fuzzy(res, data, top_n=10):
#     matches = []
    
#     # Loop through each search result
#     for search_item in res:
#         search_title = search_item.page_title.lower()
#         best_match = None
#         best_ratio = 0
        
#         # Compare with each product name in data
#         for product in data:
#             product_name = product['name'].lower()
            
#             # Calculate the similarity ratio using difflib
#             similarity_ratio = difflib.SequenceMatcher(None, product_name, search_title).ratio()
            
#             # Store the match if it's better than the current best
#             if similarity_ratio > best_ratio:
#                 best_ratio = similarity_ratio
#                 best_match = {
#                     "product_name": product['name'],
#                     "title": search_item.page_title,
#                     "site": search_item.page_url,
#                     "img": search_item.image_url,
#                     "similarity_ratio": best_ratio
#                 }
        
#         if best_match:
#             matches.append(best_match)
    
#     # Sort by similarity ratio and get top N results
#     matches = sorted(matches, key=lambda x: x['similarity_ratio'], reverse=True)[:top_n]
    
#     # Print the top N fuzzy matches
#     for match in matches:
#         print(f"Product Name: {match['product_name']}")
#         # print(f"Title: {match['title']}")
#         # print(f"Site: {match['site']}")
#         # print(f"Img: {match['img']}")
#         # print(f"Similarity Ratio: {match['similarity_ratio']:.2f}\n")

# if __name__ == '__main__':
#     # URL of the image to search
#     image_url = 'https://res.cloudinary.com/dqbnxvsrr/image/upload/v1729782847/cuahang-hb/omjh79flrgy4mmglqfws.jpg'

#     # Initialize reverse image searcher and perform search
#     rev_img_searcher = ReverseImageSearcher()
#     res = rev_img_searcher.search(image_url)
    
#     # Load data from absolute path
#     data = load_data('D:\\Do_An_Tot_Nghiep\\TImKiemGiongNoi\\Google-Reverse-Image-Search\\data2.json')

#     # Compare search results with data.json using fuzzy matching
#     compare_and_print_fuzzy(res, data, top_n=10)



import json
import difflib
from google_img_source_search import ReverseImageSearcher
from pymongo import MongoClient
import sys
from bson import ObjectId  # Nhập thư viện bson để xử lý ObjectId

# Thiết lập kết nối MongoDB
MONGODB_URI = 'mongodb+srv://khanhduc2902:khanhduc2902@cluster0.03at6jt.mongodb.net/cuahangdientu'
client = MongoClient(MONGODB_URI)
db = client['cuahangdientu']
product_collection = db['products']

# Hàm lấy dữ liệu sản phẩm từ MongoDB
def load_data_from_db():
    try:
        data = list(product_collection.find({}, {'_id': 1, 'title': 1, 'thumb': 1, 'description': 1}))  # Lấy _id và title
        return data
    except Exception as e:
        print("Error fetching data:", e)
        return []

# Hàm so sánh tiêu đề kết quả tìm kiếm với tên sản phẩm sử dụng fuzzy matching
def compare_and_print_fuzzy(res, data, top_n=10):
    matches = []
    
    for search_item in res:
        search_title = search_item.page_title.lower()  # Chuyển tiêu đề tìm kiếm về chữ thường
        best_match = None
        best_ratio = 0
        
        for product in data:
            product_name = product['title'].lower()  # Thay đổi 'name' thành 'title'
            similarity_ratio = difflib.SequenceMatcher(None, product_name, search_title).ratio()
            category_match = difflib.SequenceMatcher(None, product.get('category', '').lower(), search_item.page_title.lower()).ratio()
            category2_match = difflib.SequenceMatcher(None, product.get('category2', '').lower(), search_item.page_title.lower()).ratio()
            

            similarity_ratio = (category_match + category2_match + difflib.SequenceMatcher(None, product_name, search_title).ratio()) / 3
            
            if similarity_ratio > best_ratio:
                best_ratio = similarity_ratio
                best_match = {
                    "_id": str(product['_id']),  
                    "title": product['title'],
                    "thumb": product['thumb'],  # Lấy thumb (hình ảnh đại diện), sử dụng get để tránh KeyError
                    "description": product['description'],  # Lấy description, cũng dùng get
                    "category2": search_item.page_title,
                    "similarity_ratio": best_ratio  # Có thể giữ trường này để sắp xếp nếu cần
                }
        
        if best_match:
            matches.append(best_match)
    
    matches = sorted(matches, key=lambda x: x['similarity_ratio'], reverse=True)[:top_n]
    return matches  # Trả về danh sách kết quả

if __name__ == '__main__':
    # Lấy URL từ đối số dòng lệnh
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_url>")
        sys.exit(1)

    image_url = sys.argv[1]
    rev_img_searcher = ReverseImageSearcher()
    
    res = rev_img_searcher.search(image_url)
    data = load_data_from_db()  # Load data from MongoDB

    if not res:
        print("No results found from image search.")
        sys.exit(0)

    matches = compare_and_print_fuzzy(res, data, top_n=10)
    
    # In kết quả dưới dạng JSON
    print(json.dumps(matches))  # Xuất kết quả ra chuẩn JSON