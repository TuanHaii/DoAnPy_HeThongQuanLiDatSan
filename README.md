# Hệ thống Quản lý Đặt lịch Sân Thể Thao

Ứng dụng web quản lý đặt lịch sân thể thao được xây dựng với Django (DRF) + Django Channels, React, và MySQL.

## Tính năng chính

### Tính năng người dùng (User)
- Đăng ký/Đăng nhập tài khoản
- Xem danh sách sân thể thao (lọc theo loại, vị trí, giá)
- Xem lịch trống của từng sân theo ngày/tuần
- Tạo yêu cầu đặt sân
- Xem trạng thái booking (pending, confirmed, canceled)
- Chat trực tiếp với admin
- Xem lịch sử đặt sân và thông báo

### Tính năng Admin
- Quản lý sân (CRUD: tạo, sửa, xóa, bật/tắt hiển thị)
- Quản lý booking: xem all bookings, approve, cancel, sửa giờ
- Quản lý user: thay đổi role, khóa/mở tài khoản
- Chat với người dùng realtime
- Thống kê: lượt đặt theo ngày/tháng, doanh thu

### Tính năng hệ thống
- Xử lý xung đột đặt sân
- Lịch hiển thị rõ ràng với màu sắc phân biệt trạng thái
- Gửi thông báo khi booking thay đổi
- Chat realtime với WebSocket

## Công nghệ sử dụng

### Backend
- Django 4.2.7
- Django REST Framework
- Django Channels (WebSocket)
- Django Simple JWT (Authentication)
- MySQL
- Redis (Channel Layer & Celery)
- Celery (Background Tasks)

### Frontend
- React 18
- React Router Dom
- React Query
- Axios
- FullCalendar
- Socket.io-client
- TailwindCSS
- Vite

## Cài đặt và chạy dự án

### Yêu cầu hệ thống
- Python 3.10+
- Node.js 16+
- MySQL 8.0
- Redis

### Sử dụng Docker (Khuyến nghị)

1. Clone repository:
```bash
git clone <repository-url>
cd DoAnPy_HeThongQuanLiDatSan
```

2. Tạo file `.env`:
```bash
cp .env.example .env
# Chỉnh sửa các giá trị trong file .env
```

3. Chạy với Docker Compose:
```bash
docker-compose up -d
```

4. Tạo superuser cho admin:
```bash
docker-compose exec backend python manage.py createsuperuser
```

5. Truy cập ứng dụng:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin: http://localhost:8000/admin

### Cài đặt thủ công

#### Backend Setup

1. Tạo virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình database:
```bash
# Tạo database MySQL
mysql -u root -p
CREATE DATABASE sports_booking;
```

4. Chạy migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Tạo superuser:
```bash
python manage.py createsuperuser
```

6. Chạy server:
```bash
python manage.py runserver
```

#### Frontend Setup

1. Di chuyển vào thư mục frontend:
```bash
cd frontend
```

2. Cài đặt dependencies:
```bash
npm install
```

3. Chạy development server:
```bash
npm run dev
```

#### Redis Setup

Cài đặt và chạy Redis server để hỗ trợ WebSocket chat:
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows
# Download và cài đặt từ https://redis.io/download
```

## Cấu trúc dự án

```
DoAnPy_HeThongQuanLiDatSan/
├── backend/                    # Django project
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py                # ASGI config cho Channels
│   └── wsgi.py
├── apps/                      # Django apps
│   ├── users/                 # Quản lý user & auth
│   ├── fields/                # Quản lý sân thể thao
│   ├── bookings/              # Quản lý đặt lịch
│   ├── chat/                  # Chat realtime
│   └── notifications/         # Thông báo
├── frontend/                  # React app
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── context/          # React contexts
│   │   └── utils/            # Utilities
│   ├── package.json
│   └── vite.config.js
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker compose config
├── Dockerfile.backend         # Backend Dockerfile
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Đăng ký user
- `POST /api/auth/login/` - Đăng nhập
- `POST /api/auth/logout/` - Đăng xuất
- `POST /api/auth/token/refresh/` - Refresh token
- `GET /api/auth/profile/` - Lấy thông tin profile
- `PUT /api/auth/profile/update/` - Cập nhật profile

### Fields
- `GET /api/fields/` - Danh sách sân
- `GET /api/fields/{id}/` - Chi tiết sân
- `POST /api/fields/` - Tạo sân (admin)
- `PUT /api/fields/{id}/` - Cập nhật sân (admin)
- `DELETE /api/fields/{id}/` - Xóa sân (admin)

### Bookings
- `GET /api/bookings/` - Danh sách booking
- `POST /api/bookings/` - Tạo booking
- `GET /api/bookings/{id}/` - Chi tiết booking
- `PATCH /api/bookings/{id}/` - Cập nhật booking
- `POST /api/bookings/{id}/cancel/` - Hủy booking
- `POST /api/bookings/{id}/confirm/` - Xác nhận booking (admin)

### Chat
- `GET /api/chat/rooms/` - Danh sách chat rooms
- `POST /api/chat/rooms/` - Tạo chat room
- `GET /api/chat/rooms/{id}/` - Chi tiết chat room
- `POST /api/chat/rooms/{id}/send_message/` - Gửi tin nhắn

### WebSocket
- `ws://localhost:8000/ws/chat/{room_id}/` - WebSocket endpoint cho chat

## Đóng góp

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Liên hệ

Tuan Hai - [GitHub](https://github.com/TuanHaii)

Project Link: [https://github.com/TuanHaii/DoAnPy_HeThongQuanLiDatSan](https://github.com/TuanHaii/DoAnPy_HeThongQuanLiDatSan)