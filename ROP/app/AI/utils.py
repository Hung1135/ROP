from sentence_transformers import SentenceTransformer, util
import torch
import re
from unidecode import unidecode

# Khởi tạo model AI
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
KEYWORD_MAP = {
        'Công nghệ thông tin': [
            'it', 'lập trình', 'software', 'developer', 'dev', 'coder', 'python', 'java', 'javascript', 'php', 'c#', 'c++', 
            'ruby', 'golang', 'swift', 'kotlin', 'web', 'html', 'css', 'react', 'vue', 'angular', 'node', 'django', 'laravel',
            'mobile', 'ios', 'android', 'flutter', 'react native', 'back-end', 'backend', 'front-end', 'frontend', 'fullstack',
            'data', 'sql', 'mysql', 'mongodb', 'oracle', 'big data', 'ai', 'machine learning', 'trí tuệ nhân tạo', 'blockchain',
            'tester', 'qa', 'qc', 'automation test', 'security', 'an ninh mạng', 'hacker', 'cloud', 'aws', 'azure', 'devops',
            'system', 'hệ thống', 'mạng', 'network', 'helpdesk', 'comtor', 'brse', 'scrum', 'agile', 'game', 'unity', 'unreal'
            ,'hệ sinh thái', 'kiến trúc phần mềm', 'microservices', 'containerization', 'docker', 'kubernetes', 'triển khai', 'deploy', 'duy trì hệ thống', 'tối ưu hóa code', 'luồng dữ liệu', 'api', 'tích hợp', 'mã nguồn', 'vòng đời phần mềm', 'ux/ui'
        ],
        'Kinh doanh / Bán hàng': [
            'sale', 'kinh doanh', 'bán hàng', 'telesale', 'tele-sale', 'chăm sóc khách hàng', 'cskh', 'customer service',
            'account manager', 'am', 'bd', 'business development', 'phát triển kinh doanh', 'bất động sản', 'bds', 'thổ cư',
            'can hộ', 'môi giới', 'chốt đơn', 'tư vấn', 'salesman', 'saleswoman', 'showroom', 'cửa hàng', 'đại lý', 'phân phối',
            'thị trường', 'mở rộng thị trường', 'bán lẻ', 'retail', 'b2b', 'b2c', 'telesales', 'quầy hàng', 'siêu thị', 'doanh số', 'kpi', 'target', 'chiếm lĩnh', 'đàm phán', 'thương lượng', 'khách hàng tiềm năng', 'lead', 'phễu', 'convert', 'chuyển đổi', 'hợp đồng', 'ký kết', 'đại diện thương mại', 'đại diện nhãn hàng'
        ],
        'Marketing / Quảng cáo': [
            'marketing', 'mar', 'seo', 'sem', 'content', 'nội dung', 'copywriter', 'ads', 'quảng cáo', 'facebook ads',
            'google ads', 'tiktok ads', 'social media', 'truyền thông', 'pr', 'quan hệ công chúng', 'event', 'sự kiện',
            'brand', 'thương hiệu', 'designer', 'thiết kế', 'đồ họa', 'photoshop', 'ai', 'illustrator', 'video', 'edit',
            'capcut', 'premiere', 'quay dựng', 'kols', 'kocs', 'influencer', 'affiliate', 'email marketing', 'tổ chức sự kiện','nhận diện', 'viral', 'xu hướng', 'trending', 'insight', 'tệp khách hàng', 'segmentation', 'sáng tạo', 'visual', 'storytelling', 'kế hoạch truyền thông', 'lưu lượng truy cập', 'traffic', 'engagement', 'tương tác'
        ],
        'Tài chính / Ngân hàng': [
            'kế toán', 'ke toan', 'kiểm toán', 'tài chính', 'finance', 'ngân hàng', 'bank', 'tín dụng', 'thuế', 'tax',
            'thu ngân', 'treasury', 'kho bạc', 'chứng khoán', 'cổ phiếu', 'đầu tư', 'investment', 'phân tích tài chính',
            'cfo', 'kế toán trưởng', 'kế toán tổng hợp', 'nợ', 'công nợ', 'billing', 'thanh toán', 'giao dịch viên',
            'bảo hiểm', 'insurance', 'tư vấn tài chính', 'tổng đài ngân hàng', 'dòng tiền', 'cash flow', 'báo cáo tài chính', 'quyết toán', 'kiểm kê', 'số dư', 'phân tích rủi ro', 'vốn', 'equity', 'nợ xấu', 'tài sản', 'cân đối kế toán', 'lợi nhuận', 'p&l', 'thanh khoản'
        ],
        'Nhân sự / Hành chính': [
            'hr', 'nhân sự', 'tuyển dụng', 'recruitment', 'headhunter', 'phúc lợi', 'lương thưởng', 'c&b', 'compensation',
            'đào tạo', 'training', 'hành chính', 'admin', 'văn phòng', 'office', 'lễ tân', 'receptionist', 'thư ký',
            'secretary', 'trợ lý', 'assistant', 'văn thư', 'lưu trữ', 'pháp chế', 'legal', 'luật', 'tổng vụ', 'tổ chức'
        ],
        'Kỹ thuật / Xây dựng': [
            'kỹ thuật', 'ky thuat', 'engineer', 'kỹ sư', 'cơ khí', 'điện', 'điện tử', 'tự động hóa', 'iot', 'xây dựng',
            'construction', 'kiến trúc', 'nội thất', 'ngoại thất', 'công trình', 'giám sát', 'vận hành', 'máy móc',
            'thiết bị', 'bảo trì', 'sửa chữa', 'maintenance', 'cầu đường', 'bản vẽ', 'autocad', 'solidworks', 'revit',
            'điện lạnh', 'nhiệt', 'thủy lợi', 'trắc địa'
        ],
        'Logistics / Vận chuyển': [
            'kho', 'warehouse', 'vận chuyển', 'vận tải', 'transport', 'logistics', 'xuất nhập khẩu', 'xnk', 'import',
            'export', 'customs', 'hải quan', 'mua hàng', 'purchasing', 'procurement', 'chuỗi cung ứng', 'supply chain',
            'shipper', 'giao hàng', 'lái xe', 'tài xế', 'phụ xe', 'container', 'forwarding', 'giao nhận', 'điều phối'
        ],
        'Y tế / Dược phẩm': [
            'y tế', 'y khoa', 'bác sĩ', 'doctor', 'điều dưỡng', 'nurse', 'dược', 'pharmacy', 'dược sĩ', 'trình dược viên',
            'phòng khám', 'bệnh viện', 'nha khoa', 'thẩm mỹ viện', 'spa', 'da liễu', 'xét nghiệm', 'vật tư y tế',
            'hộ lý', 'trị liệu', 'chăm sóc sức khỏe', 'sinh học', 'lâm sàng', 'phẫu thuật', 'cấp cứu', 'x-quang', 'nội soi', 'siêu âm', 'huyết áp', 'nhịp tim', 'cơ thể', 'mô', 'tế bào', 'kháng sinh', 'vắc xin', 'liệu trình', 'phục hồi chức năng', 'vô trùng', 'chẩn đoán', 'phát đồ', 'can thiệp'

        ],
        'Giáo dục / Đào tạo': [
            'giáo dục', 'education', 'đào tạo', 'giáo viên', 'teacher', 'giảng viên', 'mentor', 'tutor', 'gia sư',
            'trung tâm tiếng anh', 'english', 'giảng dạy', 'huấn luyện viên', 'coach', 'trường học', 'mầm non',
            'tiểu học', 'thpt', 'đại học', 'học thuật', 'academic'
        ],
        'Dịch vụ / Du lịch': [
            'nhà hàng', 'khách sạn', 'hotel', 'restaurant', 'resort', 'phục vụ', 'waiter', 'waitress', 'đầu bếp',
            'chef', 'pha chế', 'barista', 'bartender', 'du lịch', 'travel', 'tour', 'hướng dẫn viên', 'vé máy bay',
            'tiếp viên', 'an ninh', 'bảo vệ', 'tạp vụ', 'buồng phòng'
        ]
    }

def clean_text(text):
    if not text: return ""
    text = text.lower()
    text = unidecode(text) 
    text = re.sub(r'[^\w\s]', ' ', text) 
    return text

def classify_job_category(title, skills, description):
    weighted_text = f"{(title + ' ') * 3} {skills} {(description + ' ') * 3}"
    cleaned_text = clean_text(weighted_text)
    
    categories_names = list(KEYWORD_MAP.keys())
    rich_category_texts = [" ".join(keywords) for keywords in KEYWORD_MAP.values()]
    
    job_embedding = model.encode(weighted_text, convert_to_tensor=True)
    category_embeddings = model.encode(rich_category_texts, convert_to_tensor=True)
    
    cosine_scores = util.cos_sim(job_embedding, category_embeddings)[0]
    top_results = torch.topk(cosine_scores, k=2)
    
    score1, idx1 = top_results.values[0].item(), top_results.indices[0].item()
    score2, idx2 = top_results.values[1].item(), top_results.indices[1].item()
    
    res1 = categories_names[idx1]
    res2 = categories_names[idx2]

    if (score1 - score2) < 0.05 or score1 < 0.40:
        count1 = sum(1 for kw in KEYWORD_MAP[res1] if kw.lower() in cleaned_text.lower())
        count2 = sum(1 for kw in KEYWORD_MAP[res2] if kw.lower() in cleaned_text.lower())
        
        if count2 > count1 and count2 > 0:
            return res2
        if count1 > 0:
            return res1

    if score1 > 0.25:
        return res1
    
    return "Ngành nghề khác"