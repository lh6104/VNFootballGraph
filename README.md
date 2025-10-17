# VNFootballGraph  
**Wikipedia-based Network of Vietnamese Football Players and Coaches**

## 🧩 Giới thiệu

**VNFootballGraph** là một dự án khai thác dữ liệu từ **Wikipedia tiếng Việt** để xây dựng **mạng lưới cầu thủ, huấn luyện viên, câu lạc bộ và đội tuyển bóng đá Việt Nam**.  
Mục tiêu là hình thành một **mạng tri thức (knowledge graph)** thể hiện mối quan hệ giữa các thực thể trong lĩnh vực bóng đá Việt Nam, phục vụ cho việc:
- Phân tích cấu trúc mạng (các cá nhân hoặc tổ chức có ảnh hưởng),
- Trực quan hóa quan hệ cầu thủ – CLB – đội tuyển,
- Làm nền tảng cho các nghiên cứu về dữ liệu mở, social graph hoặc knowledge mining.

---

## ⚙️ Ý tưởng chính

Wikipedia là một mạng liên kết tự nhiên, trong đó các trang (article) trỏ lẫn nhau qua các **internal links**.  
Tận dụng điều này, dự án sử dụng **thuật toán duyệt theo chiều rộng (BFS)** để mở rộng dần mạng tri thức bắt đầu từ một **tập node khởi đầu (seed nodes)**, bao gồm:

- Nguyễn Quang Hải (sinh 1997)  
- Công Phượng  
- Huỳnh Như  
- Đội tuyển bóng đá quốc gia Việt Nam  
- Hà Nội FC  
- Park Hang-seo  

Từ mỗi node, chương trình sẽ tự động lấy danh sách các liên kết nội bộ, lọc ra các trang có liên quan đến bóng đá Việt Nam, và tạo các cạnh (edge) giữa chúng.  
Quá trình được lặp lại đến khi đạt giới hạn về độ sâu (`MAX_DEPTH`) hoặc số lượng node (`MAX_NODES`).

---

## 🧠 Mô hình tổng quan

```
Wikipedia Dump / API
↓
Seed Nodes (Players, Clubs, Teams, Coaches)
↓
Auto Expansion (BFS)
↓
NetworkX Graph (Directed)
↓
Export:
├── JSON (Node-Link)
├── GEXF / GraphML (for Gephi)
├── CSV (Edges / Nodes)
└── Adjacency Matrix (CSV, XLSX, NPY)
```


---

## 🧰 Công cụ sử dụng

| Thành phần | Mục đích | Ghi chú |
|-------------|-----------|---------|
| **Python 3.10+** | Lập trình chính | |
| **Wikipedia-API** | Truy cập dữ liệu Wikipedia tiếng Việt | `pip install wikipedia-api` |
| **NetworkX** | Xây dựng và xử lý đồ thị | `pip install networkx` |
| **pandas / numpy** | Xử lý dữ liệu và ma trận | |
| **pyvis** *(tùy chọn)* | Xuất đồ thị tương tác HTML | |
| **Gephi** *(ngoài Python)* | Trực quan hóa mạng lưới | |

---

## 🏗️ Cấu trúc thư mục
```
VNFootballGraph/
│
├── src/
│ ├── 01_download_articles.py # Thu thập dữ liệu từ Wikipedia
│ ├── 02_expand_graph.ipynb # Notebook mở rộng mạng và tạo đồ thị
│ ├── 03_matrix_export.ipynb # Xuất ma trận kề và phân tích
│ └── utils/ # Các hàm hỗ trợ
│
├── data/
│ ├── seed_nodes.json # Danh sách node khởi đầu (hạt giống)
│ ├── auto_expanded_nodes.csv # Node thu được
│ ├── auto_expanded_edges.csv # Các cạnh trong đồ thị
│ └── graph_exports/
│ ├── VNFootballGraph.gexf
│ ├── VNFootballGraph.graphml
│ ├── VNFootballGraph.json
│ └── matrix/
│ ├── adjacency_matrix.csv
│ ├── adjacency_matrix.xlsx
│ └── adjacency_matrix.npy
│
├── README.md
└── requirements.txt

```


---

## 🚀 Cách chạy

### 1. Tạo môi trường Python
```bash
conda create -n vnfootball python=3.10
conda activate vnfootball
pip install wikipedia-api networkx pandas numpy tqdm pyvis matplotlib
```

### 2. Chạy notebook chính
```
jupyter notebook src/02_expand_graph.ipynb
```

