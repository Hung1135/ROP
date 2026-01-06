from sentence_transformers import SentenceTransformer, util
import torch

# Chọn model nhẹ nhất cho đa ngôn ngữ để tránh treo máy
# Model này nặng khoảng 420MB
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def classify_job_category(title, skills, description):
    job_text = f"{title} {skills} {description}"
    
    # Danh sách các ngành nghề mục tiêu
    categories = [
        'Công nghệ thông tin', 
        'Kinh doanh / Bán hàng', 
        'Marketing / Quảng cáo', 
        'Tài chính / Ngân hàng',
        'Nhân sự / Hành chính',
        'Kỹ thuật / Xây dựng',
        'Y tế / Dược phẩm',
        'Giáo dục / Đào tạo'
    ]
    
    # 1. Chuyển mô tả công việc thành vector
    job_embedding = model.encode(job_text, convert_to_tensor=True)
    
    # 2. Chuyển danh sách ngành nghề thành vector
    category_embeddings = model.encode(categories, convert_to_tensor=True)
    
    # 3. Tính độ tương đồng (Cosine Similarity)
    cosine_scores = util.cos_sim(job_embedding, category_embeddings)[0]
    
    # 4. Lấy ngành nghề có điểm cao nhất
    best_match_idx = torch.argmax(cosine_scores).item()
    
    # Chỉ lấy nếu độ tin tưởng > 0.4 (tránh đoán bừa)
    if cosine_scores[best_match_idx] > 0.4:
        return categories[best_match_idx]
    
    return "Ngành nghề khác"
# def classify_job_category(title, skills, description):
#     # Gộp và làm sạch text
#     text = f"{title} {skills} {description}".lower()
    
#     categories = {
#         'Công nghệ thông tin': [
#             'it', 'lập trình', 'software', 'developer', 'dev', 'coder', 'python', 'java', 'javascript', 'php', 'c#', 'c++', 
#             'ruby', 'golang', 'swift', 'kotlin', 'web', 'html', 'css', 'react', 'vue', 'angular', 'node', 'django', 'laravel',
#             'mobile', 'ios', 'android', 'flutter', 'react native', 'back-end', 'backend', 'front-end', 'frontend', 'fullstack',
#             'data', 'sql', 'mysql', 'mongodb', 'oracle', 'big data', 'ai', 'machine learning', 'trí tuệ nhân tạo', 'blockchain',
#             'tester', 'qa', 'qc', 'automation test', 'security', 'an ninh mạng', 'hacker', 'cloud', 'aws', 'azure', 'devops',
#             'system', 'hệ thống', 'mạng', 'network', 'helpdesk', 'comtor', 'brse', 'scrum', 'agile', 'game', 'unity', 'unreal'
#         ],
#         'Kinh doanh / Bán hàng': [
#             'sale', 'kinh doanh', 'bán hàng', 'telesale', 'tele-sale', 'chăm sóc khách hàng', 'cskh', 'customer service',
#             'account manager', 'am', 'bd', 'business development', 'phát triển kinh doanh', 'bất động sản', 'bds', 'thổ cư',
#             'can hộ', 'môi giới', 'chốt đơn', 'tư vấn', 'salesman', 'saleswoman', 'showroom', 'cửa hàng', 'đại lý', 'phân phối',
#             'thị trường', 'mở rộng thị trường', 'bán lẻ', 'retail', 'b2b', 'b2c', 'telesales', 'quầy hàng', 'siêu thị'
#         ],
#         'Marketing / Quảng cáo': [
#             'marketing', 'mar', 'seo', 'sem', 'content', 'nội dung', 'copywriter', 'ads', 'quảng cáo', 'facebook ads',
#             'google ads', 'tiktok ads', 'social media', 'truyền thông', 'pr', 'quan hệ công chúng', 'event', 'sự kiện',
#             'brand', 'thương hiệu', 'designer', 'thiết kế', 'đồ họa', 'photoshop', 'ai', 'illustrator', 'video', 'edit',
#             'capcut', 'premiere', 'quay dựng', 'kols', 'kocs', 'influencer', 'affiliate', 'email marketing', 'tổ chức sự kiện'
#         ],
#         'Tài chính / Ngân hàng': [
#             'kế toán', 'ke toan', 'kiểm toán', 'tài chính', 'finance', 'ngân hàng', 'bank', 'tín dụng', 'thuế', 'tax',
#             'thu ngân', 'treasury', 'kho bạc', 'chứng khoán', 'cổ phiếu', 'đầu tư', 'investment', 'phân tích tài chính',
#             'cfo', 'kế toán trưởng', 'kế toán tổng hợp', 'nợ', 'công nợ', 'billing', 'thanh toán', 'giao dịch viên',
#             'bảo hiểm', 'insurance', 'tư vấn tài chính', 'tổng đài ngân hàng'
#         ],
#         'Nhân sự / Hành chính': [
#             'hr', 'nhân sự', 'tuyển dụng', 'recruitment', 'headhunter', 'phúc lợi', 'lương thưởng', 'c&b', 'compensation',
#             'đào tạo', 'training', 'hành chính', 'admin', 'văn phòng', 'office', 'lễ tân', 'receptionist', 'thư ký',
#             'secretary', 'trợ lý', 'assistant', 'văn thư', 'lưu trữ', 'pháp chế', 'legal', 'luật', 'tổng vụ', 'tổ chức'
#         ],
#         'Kỹ thuật / Xây dựng': [
#             'kỹ thuật', 'ky thuat', 'engineer', 'kỹ sư', 'cơ khí', 'điện', 'điện tử', 'tự động hóa', 'iot', 'xây dựng',
#             'construction', 'kiến trúc', 'nội thất', 'ngoại thất', 'công trình', 'giám sát', 'vận hành', 'máy móc',
#             'thiết bị', 'bảo trì', 'sửa chữa', 'maintenance', 'cầu đường', 'bản vẽ', 'autocad', 'solidworks', 'revit',
#             'điện lạnh', 'nhiệt', 'thủy lợi', 'trắc địa'
#         ],
#         'Logistics / Vận chuyển': [
#             'kho', 'warehouse', 'vận chuyển', 'vận tải', 'transport', 'logistics', 'xuất nhập khẩu', 'xnk', 'import',
#             'export', 'customs', 'hải quan', 'mua hàng', 'purchasing', 'procurement', 'chuỗi cung ứng', 'supply chain',
#             'shipper', 'giao hàng', 'lái xe', 'tài xế', 'phụ xe', 'container', 'forwarding', 'giao nhận', 'điều phối'
#         ],
#         'Y tế / Dược phẩm': [
#             'y tế', 'y khoa', 'bác sĩ', 'doctor', 'điều dưỡng', 'nurse', 'dược', 'pharmacy', 'dược sĩ', 'trình dược viên',
#             'phòng khám', 'bệnh viện', 'nha khoa', 'thẩm mỹ viện', 'spa', 'da liễu', 'xét nghiệm', 'vật tư y tế',
#             'hộ lý', 'trị liệu', 'chăm sóc sức khỏe'
#         ],
#         'Giáo dục / Đào tạo': [
#             'giáo dục', 'education', 'đào tạo', 'giáo viên', 'teacher', 'giảng viên', 'mentor', 'tutor', 'gia sư',
#             'trung tâm tiếng anh', 'english', 'giảng dạy', 'huấn luyện viên', 'coach', 'trường học', 'mầm non',
#             'tiểu học', 'thpt', 'đại học', 'học thuật', 'academic'
#         ],
#         'Dịch vụ / Du lịch': [
#             'nhà hàng', 'khách sạn', 'hotel', 'restaurant', 'resort', 'phục vụ', 'waiter', 'waitress', 'đầu bếp',
#             'chef', 'pha chế', 'barista', 'bartender', 'du lịch', 'travel', 'tour', 'hướng dẫn viên', 'vé máy bay',
#             'tiếp viên', 'an ninh', 'bảo vệ', 'tạp vụ', 'buồng phòng'
#         ]
#     }

#     # Quét từng nhóm ngành
#     for category, keywords in categories.items():
#         if any(kw in text for kw in keywords):
#             return category
    
#     return "Ngành nghề khác"