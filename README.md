# TradingAgents: Multi-Agents LLM Financial Trading Framework

  **TradingAgents** là một framework giao dịch chứng khoán tiên tiến, mô phỏng cấu trúc vận hành của một quỹ đầu tư thực tế thông qua sự phối hợp của nhiều tác nhân (agents) được vận hành bởi các mô hình ngôn ngữ lớn (LLMs). Hệ thống này không chỉ tập trung vào việc đưa ra quyết định giao dịch mà còn ưu tiên tính giải thích được (explainability) và quản trị rủi ro chặt chẽ.

## 🚀 Tính năng nổi bật
- Mô phỏng tổ chức thực tế: Hệ thống gồm 7 vai trò chuyên biệt: Phân tích cơ bản, Phân tích kỹ thuật, Phân tích tâm lý, Phân tích tin tức, Nghiên cứu viên, Nhà giao dịch và Quản lý rủi ro.
- Cơ chế tranh luận (Agentic Debate): Các agents thuộc nhóm Nghiên cứu viên (Bullish vs Bearish) sẽ tranh luận để đưa ra cái nhìn khách quan nhất về thị trường.
- Giao thức truyền thông cấu trúc: Thay vì chỉ sử dụng hội thoại tự do, framework sử dụng các báo cáo có cấu trúc để tránh hiện tượng "tam sao thất bản" (telephone effect) khi xử lý tác vụ dài hạn.
- Hỗ trợ đa mô hình: Tối ưu hóa việc sử dụng kết hợp các mô hình "tư duy nhanh" (GPT-4o-mini) cho việc lấy dữ liệu và mô hình "tư duy sâu" (o1-preview) cho việc ra quyết định.

## 🏗 Kiến trúc hệ thống
Hệ thống vận hành qua 5 bước chính:
1. **ANALYSTS TEAM:** Thu thập dữ liệu từ Yahoo Finance, Reddit, Bloomberg, Reuters....
2. **RESEARCH TEAM:** Tranh luận đa chiều giữa góc nhìn tích cực (Bullish) và tiêu cực (Bearish).
3. **TRADER:** Tổng hợp phân tích để đưa ra tín hiệu Giao dịch (Mua/Bán/Giữ).
4. **RISK MANAGEMENT:** Đánh giá rủi ro dựa trên các kịch bản thận trọng, trung lập và mạo hiểm.
5. **FUND MANAGER:** Phê duyệt cuối cùng và thực thi giao dịch.

## 📈 Kết quả thử nghiệm
Trong các đợt backtest (01/2024 - 03/2024) với các mã cổ phiếu công nghệ lớn (AAPL, NVDA, MSFT...):
- Lợi nhuận tích lũy: Đạt ít nhất **23.21%**, vượt xa các phương pháp truyền thống như MACD hay SMA.
- Chỉ số Sharpe: Thể hiện khả năng tối ưu hóa lợi nhuận trên đơn vị rủi ro vượt trội.
- Khả năng giải thích: Mọi quyết định đều đi kèm với nhật ký suy luận bằng ngôn ngữ tự nhiên.

## 🛠 Cài đặt
Hướng dẫn cài đặt: 
git clone https://github.com/anh922006/Trading-Agent.git
cd Trading-Agent
python -m venv venv  #cài môi trường ảo
venv\Scripts\activate
pip install -r requirements.txt

## Các ký hiệu Git trong VS Code:
U (xanh) = Untracked - file mới chưa add
M (cam) = Modified - file đã sửa đổi
A (xanh lá) = Added - file mới đã add vào staging
D (đỏ) = Deleted - file đã xóa
C = Conflict - xung đột khi merge
R = Renamed - file đổi tên

## Cách bước lấy dữ liệu đẩy dữ liệu
1. git pull origin main # Lấy code mới nhất từ GitHub về máy Khi code xong nên pull lại 1 lần nữa để đồng bộ code của cả nhóm (làm lại bước 1)
2. git add . # Thêm file bạn vừa sửa / cập nhật code vừa mình làm
3. git commit -m "Cập nhật phần ... của Thành viên 1|2|3..."
4. git push origin main # Đẩy code lên GitHub 