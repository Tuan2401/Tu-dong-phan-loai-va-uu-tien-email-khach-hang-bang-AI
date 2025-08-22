from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import datetime
import pytz
from lay_email import lay_email_gmail
from gui_email import send_email
from flask import jsonify
# from send_email import send_email  # nếu có module gửi email riêng thì import ở đây

app = Flask(__name__)
app.secret_key = "secret_key_ai_email"

# Lưu tài khoản đăng nhập tạm thời (demo, không dùng CSDL)
users = {}

# ---------------------------
# Hàm gợi ý phản hồi
# ---------------------------
def goi_y_phan_hoi(loai_email, noi_dung):
    if loai_email.lower() == "khiếu nại":
        return (
            "Xin lỗi anh/chị vì sự bất tiện trong quá trình sử dụng dịch vụ. "
            "Chúng tôi sẽ tìm giải pháp phù hợp để xử lý: "
            f"{noi_dung}. "
            "Anh/chị vui lòng cung cấp thêm thông tin chi tiết để chúng tôi hỗ trợ nhanh chóng nhất."
        )
    elif loai_email.lower() == "góp ý":
        return (
            "Cảm ơn anh/chị đã góp ý. "
            "Chúng tôi trân trọng và sẽ xem xét để cải thiện dịch vụ."
        )
    elif loai_email.lower() == "hỏi đáp":
        return (
            "Xin cảm ơn anh/chị đã quan tâm. "
            f"Về vấn đề anh/chị hỏi: {noi_dung}. "
            "Nếu cần thêm thông tin, anh/chị vui lòng phản hồi lại email này."
        )
    elif loai_email.lower() == "đặt hàng":
        return (
            "Để đặt hàng nhanh chóng và tiện lợi, anh/chị vui lòng truy cập gian hàng chính thức "
            "của chúng tôi tại Shopee: https://shopee.vn/shop/123456. "
            "Rất hân hạnh được phục vụ anh/chị."
        )
    else:
        return "Xin cảm ơn anh/chị đã liên hệ. Chúng tôi sẽ phản hồi sớm nhất."


# ---------------------------
# Hàm lấy email đã xử lý
# ---------------------------
def lay_email_da_xu_ly(duong_dan_file="email_gmail_sach.csv", thoi_gian="tatca", uu_tien_loc="tatca"):
    try:
        df = pd.read_csv(duong_dan_file, encoding="utf-8")
        df = df.dropna(subset=["TieuDe", "NoiDung"])
        danh_sach_gmail = lay_email_gmail(maxResults=len(df), save_csv=False)
        now = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))

        emails = []
        for idx, row in enumerate(df.itertuples()):
            loai = str(row.TieuDe).strip()
            noi_dung = str(row.NoiDung).strip()
            phan_loai = getattr(row, "PhanLoai", "")

            try:
                email_api = danh_sach_gmail[idx]
                email_khach = email_api["EmailNguoiGui"]
                thoi_gian_gui = pd.to_datetime(email_api["ThoiGianGui"])
            except IndexError:
                email_khach = ""
                thoi_gian_gui = None

            # Lọc theo thời gian
            if thoi_gian_gui:
                if thoi_gian == "homnay" and thoi_gian_gui.date() != now.date():
                    continue
                elif thoi_gian == "tuan":
                    tuan_dau = now - datetime.timedelta(days=now.weekday())
                    tuan_cuoi = tuan_dau + datetime.timedelta(days=6)
                    if not (tuan_dau.date() <= thoi_gian_gui.date() <= tuan_cuoi.date()):
                        continue
                elif thoi_gian == "thang" and (thoi_gian_gui.month != now.month or thoi_gian_gui.year != now.year):
                    continue

            # Xác định mức độ ưu tiên
            if "khiếu nại" in loai.lower():
                uu_tien = "Cao"
            elif "đặt hàng" in loai.lower():
                uu_tien = "Trung bình"
            else:
                uu_tien = "Thấp"

            # Áp dụng lọc theo uu_tien_loc
            if uu_tien_loc != "tatca" and uu_tien.lower() != uu_tien_loc.lower():
                continue

            # Gợi ý phản hồi (theo loại email)
            goiy = goi_y_phan_hoi(loai, noi_dung)

            emails.append({
                "stt": idx + 1,
                "tieu_de": loai,
                "noi_dung": noi_dung,
                "email_khach": email_khach,
                "thoi_gian_gui": thoi_gian_gui.strftime("%d-%m-%Y %H:%M") if thoi_gian_gui else "",
                "phan_loai": phan_loai,
                "uu_tien": uu_tien,
                "goiy": goiy,
                "hanh_dong": ""
            })
        return emails
    except Exception as e:
        print(f"Lỗi khi xử lý email: {e}")
        return []


# ---------------------------
# Trang đăng nhập
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            error = "Tên đăng nhập hoặc mật khẩu không đúng!"
            return render_template("login.html", error=error)
    return render_template("login.html", error=None)


# ---------------------------
# Trang đăng ký
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if username in users:
            error = "Tên đăng nhập đã tồn tại!"
            return render_template("register.html", error=error)
        elif password != confirm:
            error = "Mật khẩu nhập lại không khớp!"
            return render_template("register.html", error=error)
        else:
            users[username] = password
            return redirect(url_for("login"))
    return render_template("register.html", error=None)


# ---------------------------
# Đăng xuất
# ---------------------------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# ---------------------------
# Trang chủ
# ---------------------------
@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    thoi_gian = request.args.get("thoigian", "tatca")
    uu_tien_loc = request.args.get("uutiens", "tatca")
    emails = lay_email_da_xu_ly(thoi_gian=thoi_gian, uu_tien_loc=uu_tien_loc)
    return render_template(
        "trang_chu.html",
        emails=emails,
        current_year=datetime.datetime.now().year,
        thoi_gian=thoi_gian,
        uu_tien_loc=uu_tien_loc
    )


# ---------------------------
# Làm mới Gmail
# ---------------------------
@app.route("/refresh")
def refresh():
    if "username" not in session:
        return redirect(url_for("login"))
    lay_email_gmail()
    return redirect(url_for("index"))


# ---------------------------
# Trả lời ngay
# ---------------------------
@app.route("/reply/<int:stt>", methods=["POST"])
def reply(stt):
    if "username" not in session:
        return redirect(url_for("login"))

    # Lấy email tạm thời từ form (hoặc bạn có thể lưu email vào session nếu muốn)
    nguoi_nhan = request.form.get("email_khach", "")
    noi_dung_gui = request.form.get("goiy", "")

    if nguoi_nhan and noi_dung_gui:
        try:
            # TODO: tích hợp SMTP hoặc Gmail API
            # send_email(to=nguoi_nhan, subject="Phản hồi từ CSKH", body=noi_dung_gui)
            print(f"Đã gửi email đến {nguoi_nhan}: {noi_dung_gui}")
            flash(f"✅ Đã gửi phản hồi đến {nguoi_nhan}", "success")
        except Exception as e:
            flash(f"Lỗi khi gửi email: {e}", "danger")
    else:
        flash("Không tìm thấy email hoặc nội dung phản hồi!", "warning")

    return redirect(url_for("index"))

@app.route("/reply_ajax/<int:stt>", methods=["POST"])
def reply_ajax(stt):
    if "username" not in session:
        return jsonify({"status": "error", "message": "Bạn chưa đăng nhập!"})

    # Lấy danh sách email đã xử lý
    emails = lay_email_da_xu_ly()
    email = next((e for e in emails if e["stt"] == stt), None)

    if not email:
        return jsonify({"status": "error", "message": "Không tìm thấy email!"})

    nguoi_nhan = email["email_khach"]
    noi_dung_gui = email["goiy"]
    tieu_de = f"Phản hồi: {email['tieu_de']}"

    # Gửi email
    success, msg = send_email(nguoi_nhan, tieu_de, noi_dung_gui)
    if success:
        return jsonify({"status": "success", "message": msg})
    else:
        return jsonify({"status": "error", "message": f"Lỗi khi gửi email: {msg}"})

# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
