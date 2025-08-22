import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import seaborn as sns
import matplotlib.pyplot as plt

# ------------------------------
# 1️⃣ Đọc dữ liệu CSV
# ------------------------------
du_lieu = pd.read_csv('D:\\NAMBA\\ChuyenDoiSo\\Email_AI\\data\\email_training.csv')

print("Số lượng email trong dữ liệu:", len(du_lieu))
print("Các nhãn có trong dữ liệu:", du_lieu['Nhan'].unique())
print("5 email đầu tiên:\n", du_lieu.head(), "\n")

# ------------------------------
# 2️⃣ Tiền xử lý nội dung
# ------------------------------
def tien_xu_ly(text):
    text = str(text).lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\r', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

du_lieu['NoiDung'] = du_lieu['NoiDung'].apply(tien_xu_ly)

# ------------------------------
# 3️⃣ Chuẩn bị dữ liệu train/test
# ------------------------------
X = du_lieu['NoiDung']
y = du_lieu['Nhan']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Bắt đầu train mô hình với {len(X_train)} email train và {len(X_test)} email test\n")

# ------------------------------
# 4️⃣ Pipeline TF-IDF + Naive Bayes
# ------------------------------
mo_hinh = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
    ('nb', MultinomialNB(alpha=0.1))
])

# ------------------------------
# 5️⃣ Train mô hình
# ------------------------------
mo_hinh.fit(X_train, y_train)
print("✅ Train xong, bắt đầu đánh giá mô hình...\n")

# ------------------------------
# 6️⃣ Đánh giá mô hình
# ------------------------------
y_pred = mo_hinh.predict(X_test)

print("📊 Báo cáo phân loại chi tiết:\n")
print(classification_report(y_test, y_pred, digits=4))

print("📌 Ma trận nhầm lẫn:\n")
cm = confusion_matrix(y_test, y_pred, labels=du_lieu['Nhan'].unique())
print(cm)

# ------------------------------
# 7️⃣ Vẽ ma trận nhầm lẫn trực quan
# ------------------------------
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=du_lieu['Nhan'].unique(),
            yticklabels=du_lieu['Nhan'].unique())
plt.ylabel('Nhãn thật')
plt.xlabel('Nhãn dự đoán')
plt.title('Ma trận nhầm lẫn trực quan')
plt.show()

# ------------------------------
# 8️⃣ Lưu mô hình
# ------------------------------
joblib.dump(mo_hinh, 'D:\\NAMBA\\ChuyenDoiSo\\Email_AI\\mo_hinh_email.pkl')
print("Mô hình đã được lưu")
