import pandas as pd
import joblib
from sklearn.pipeline import Pipeline

# ======== Load mô hình ========
mo_hinh = joblib.load("mo_hinh_email.pkl")

# ======== Load email mới ========
df_email = pd.read_csv("email_da_lam_sach.csv")

# ======== Dự đoán ========
noi_dung = df_email['NoiDung']
df_email['NhanDuDoan'] = mo_hinh.predict(noi_dung)

# ======== Lưu kết quả ========
df_email.to_csv("ket_qua_email.csv", index=False, encoding="utf-8")
print("✅ Đã lưu kết quả dự đoán vào ket_qua_email.csv")
