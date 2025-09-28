import React from 'react'

const Home = () => {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Chào mừng đến với Hệ thống Quản lý Đặt lịch Sân Thể Thao
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Quick stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Tổng số sân
            </h3>
            <p className="text-3xl font-bold text-primary-600">12</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Lượt đặt hôm nay
            </h3>
            <p className="text-3xl font-bold text-success-600">8</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Đang hoạt động
            </h3>
            <p className="text-3xl font-bold text-warning-600">5</p>
          </div>
        </div>

        {/* Recent bookings or popular fields */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Sân phổ biến
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow overflow-hidden">
                <div className="h-48 bg-gray-200"></div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Sân bóng đá {i}
                  </h3>
                  <p className="text-gray-600 mb-2">Địa chỉ mẫu {i}</p>
                  <p className="text-primary-600 font-bold">
                    200,000 VNĐ/giờ
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home