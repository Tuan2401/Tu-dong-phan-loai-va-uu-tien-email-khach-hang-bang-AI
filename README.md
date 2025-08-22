🚀 Giới thiệu

      Trong thời đại chuyển đổi số, doanh nghiệp nhận được số lượng lớn email từ khách hàng mỗi ngày (khiếu nại, đặt hàng, phản hồi, hỗ trợ kỹ thuật…). Việc xử lý thủ công gây tốn thời gian và dễ bỏ sót email quan trọng.
      
      Đề tài "Tự động phân loại và ưu tiên email khách hàng bằng AI" nhằm xây dựng một hệ thống sử dụng Xử lý ngôn ngữ tự nhiên (NLP) và Thuật toán học máy để:
      
      Phân loại email theo nhóm (khiếu nại, đặt hàng, hỗ trợ, phản hồi...).
      
      Ưu tiên email quan trọng để nhân viên chăm sóc khách hàng xử lý nhanh hơn.
      
      Tích hợp hệ thống vào quy trình CRM/Dịch vụ khách hàng.

🛠️ Công nghệ sử dụng

  Ngôn ngữ: Python 3.x
    
 Thư viện chính:
    
          scikit-learn: TF-IDF, mô hình phân loại (Naive Bayes, SVM, Logistic Regression).
          
          nltk, underthesea: Tiền xử lý ngôn ngữ (tokenization, stemming, stopwords).
          
          Flask: Xây dựng giao diện web.
          
          pandas, numpy: Xử lý dữ liệu.
          
 CSDL: SQLite / MySQL (lưu trữ email và kết quả phân loại).
          
Triển khai: có thể chạy trên Cloud (AWS, GCP, Azure).

📊 Quy trình hệ thống

Thu thập dữ liệu

    Lấy email từ Gmail IMAP/Outlook API.

    Tập dữ liệu mẫu gồm: khiếu nại, đặt hàng, phản hồi, hỗ trợ.

Tiền xử lý

    Chuẩn hóa văn bản (xóa ký tự đặc biệt, chuẩn hóa Unicode).

    Tokenization (cắt từ tiếng Việt/tiếng Anh).

    Loại bỏ stopwords.

Trích xuất đặc trưng

    Áp dụng TF-IDF để biểu diễn email thành vector.

Huấn luyện mô hình

    Dùng các thuật toán phân loại: Naive Bayes, SVM, Logistic Regression.

    Đánh giá mô hình bằng Precision, Recall, F1-score.

Phân loại & Ưu tiên

    Email được phân loại theo nhãn (khiếu nại, đặt hàng, hỗ trợ…).

    Tự động gán mức Ưu tiên (cao / trung bình / thấp) dựa trên nội dung.

Triển khai ứng dụng

    Giao diện web Flask hiển thị danh sách email, nhãn phân loại, mức ưu tiên.

    Tích hợp với hệ thống CRM để hỗ trợ CSKH.
📷 Minh họa giao diện (ví dụ)

Trang chủ: hiển thị danh sách email + nhãn phân loại.

Chi tiết email: hiển thị nội dung + lý do phân loại + mức ưu tiên.

Thống kê: biểu đồ số lượng email theo từng loại.
