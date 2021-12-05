import math

from django.conf import settings

from service.utils import requests_retry_session


class NoiBaiConnectAPI(object):
    """
    This service use NoiBaiConnect API for price quotations & bookings
    """

    def call_api(self, method, url, data):
        try:
            send_request = getattr(requests_retry_session(), method)
            resp = send_request(url, params=data, timeout=11).json()
        except Exception:
            return {}, 500
        else:
            if resp["status"] is True:
                return resp["data"], 200
            return resp["message"], 400

    def get_price(self, data):
        """
        ___
        **Method:** GET
        ___
        **Input:**
        - `trip_distance` (default 0, type: meter): tổng độ dài chuyến đi (chiều đi), bao gồm các điểm dừng
        - `trip_duration`(default 0, type: second): thời gian di chuyển chuyến đi (chiều đi), bao gồm các điểm dừng
        - `trip_type` (default 0, type: number): 0 nếu là chuyến tiễn (đến sân bay), 1 nếu là chuyến đón (từ sân bay đi)
        - `num_stop_points` (default 0, type: number): số điểm dừng
        - `num_seats` (default 4, type: number): số chỗ
        - `wait_time` (default 0, type: hour): tổng số giờ xe phải đợi
        - `is_round_trip` (default false): chuyến đi hai chiều
        - `is_long_distance_trip` (default false): chuyến đi đường dài
        - `return_trip_distance` (default 0, type: meter): tổng độ dài chuyến về, bao gồm các điểm dừng
        - `pickup_time` (default empty string, format: 'HH:ii:ss): thời gian đón

        ___
        **Output:**
        - `status`: *true* server đã tính toán và trả về kết quả, *false* cho các trường hợp còn lại
        - `message`: lý do cho `status` có giá trị *false*
        - `data`:
            - `trip_distance`
            - `num_stop_points`
            - `trip_type`
            - `num_seats`
            - `wait_time`
            - `is_round_trip`
            - `is_long_distance_trip`
            - `return_trip_distance`
            - `pickup_time`
            - `trip_duration`
            - `stop_fee`: phụ phí điểm dừng (đơn vị: VND)
            - `night_fee`: phụ phí chuyến đêm (đơn vị: VND)
            - `wait_fee`: phụ phí chờ (đơn vị: VND)
            - `total_fee`: tổng tiền (bao gồm mọi phụ phí)
            - `commission`: mức hoa hồng cắt cho đối tác

        ___
        **Demo url:**

        http://api.noibaiconnect.com/api/v1/map/price?trip_distance=28880&pickup_time=00:45:00
        """
        list_key = [
            "trip_distance",
            "trip_duration",
            "trip_type",
            "num_stop_points",
            "num_seats",
            "wait_time",
            "is_round_trip",
            "is_long_distance_trip",
            "return_trip_distance",
        ]
        json_data = {
            k: data[k]
            for k in list_key
            if k in data
        }

        json_data["pickup_time"] = data['pickup_datetime'].strftime("%H:%M:%S")
        return self.call_api("get", settings.NOIBAICONNECT_QUOTATION_URL, json_data)

    def book_a_trip(self, data):
        """
        **Base URI:** http://api.noibaiconnect.com/api/v1/nbc
        ___
        **Method:** POST
        ___
        **Input:**
        - `quoted_price` (required|number|min:0): giá đã báo nhận được từ **Output** của [Get Price API](%5BNBC%5D-Get-price-API). Con số này chỉ để backend của NBC tham khảo.
        - `start_point` (required|min:3): điểm xuất phát
        - `end_point` (required|min:3): điểm cuối, nếu điểm cuối là Nội Bài, để giá trị là noi bai, ha noi, viet nam
        - `stop_points` (nullable|string): danh sách điểm dừng giữa đường (nếu có), cách nhau bởi dấu **;**
        - `num_seats` (required|number|min:4): số chỗ
        - `pickup_datetime` (required|date): thời gian đón
        - `wait_time` (default 0, nullable|number): số giờ chờ
        - `is_round_trip` (default false, nullable): *true* nếu là hai chiều, các các giá trị còn lại đều là 1 chiều
        - `is_long_distance_trip` (default false, nullable): *true* nếu là đường dài, các các giá trị còn lại đều không phải đường dài
        - `stop_fee`: phụ phí điểm dừng (đơn vị: VND)
        - `night_fee`: phụ phí chuyến đêm
        - `wait_fee`: phụ phí chờ
        - `trip_type` (required|number): 0 chuyến tiễn, 1 chuyến đón, 2 đường dài

        (lý do vì sao phải có `stop_fee`, `night_fee`, `wait_fee`, `trip_type `khi đã có `total_fee` vì đây là thông tin hỗ trợ tổng đài khi nói chuyện với khách)
        ___
        **Output:**
        - `status`: *true* thao tác thành công, *false* cho các trường hợp còn lại
        - `message`: lý do cho `status` có giá trị *false*, nếu đối với validation sẽ có chi tiết các lỗi trong errors, ví dụ
        - `data`:
            - `order_id`
            - `quoted_price`
            - `start_point`
            - `end_point`
            - `stop_points`
            - `num_seats`
            - `pickup_datetime`
            - `wait_time`
            - `is_round_trip`
            - `is_long_distance_trip`
            - `trip_type`
            - `stop_fee`: phụ phí điểm dừng (đơn vị: VND)
            - `night_fee`: phụ phí chuyến đêm
            - `wait_fee`: phụ phí chờ
            - `commission`: mức hoa hồng cắt cho đối tác

        (mọi phụ phí và số tiền đều là VND)
        """
        list_key = {
            "start_point",
            "end_point",
            "stop_points",
            "num_seats",
            "wait_time",
            "is_round_trip",
            "is_long_distance_trip",
            "stop_fee",
            "night_fee",
            "wait_fee",
            "trip_type",
            "pickup_datetime",
            "customer_name",
            "customer_phone",
            "note",
        }
        json_data = {
            k: data[k]
            for k in list_key
            if k in data
        }

        json_data["reference"] = "Mebaha order #{}".format(data["id"])
        json_data["wait_time"] = math.ceil(json_data["wait_time"])
        json_data["quoted_price"] = data["total_fee"]

        data, status = self.call_api("post", settings.NOIBAICONNECT_BOOKING_URL, json_data)
        if status == 200 and "quoted_price" in data:
            data["total_fee"] = data["quoted_price"]

        return data, status

    def check_booking_status(self, order_ids):
        """
        **Base URI:** http://api.noibaiconnect.com/api/v0/map/track
        ___
        **Method:** GET
        ___
        **Input:**
        - `order_ids` (required|number|min:0): giá đã báo nhận được từ **Output** của [Get Price API](%5BNBC%5D-Get-price-API). Con số này chỉ để backend của NBC tham khảo.
        ___
        **Output:**
        - `status`: *true* thao tác thành công, *false* cho các trường hợp còn lại
        - `message`: lý do cho `status` có giá trị *false*, nếu đối với validation sẽ có chi tiết các lỗi trong errors, ví dụ
        - `data`:
            - `order_status`: { "name": "completed" }

        (mọi phụ phí và số tiền đều là VND)
        """
        json_data = {
            'order_ids': ",".join(order_ids)
        }
        data, status = self.call_api("get", settings.NOIBAICONNECT_BOOKING_STATUS_URL, json_data)
        return data, status
