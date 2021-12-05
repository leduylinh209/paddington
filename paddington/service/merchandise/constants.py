ORDER_STATUS = (
    ("new", "1. Chờ xác nhận"),
    ("confirmed", "2. Đã xác nhận"),
    ("ready_to_ship", "3. Sẵn sàng giao hàng"),
    ("dispatched", "4. Đã giao hàng cho shipper"),
    ("shipping", "5. Shipper đang giao hàng"),
    ("delivered", "6. Đã giao hàng cho người nhận"),
    ("completed", "7. Đã hoàn thành và thanh toán"),
    ("cancelled", "8. Đã huỷ"),
    ("problem", "9. Gặp vấn đề"),
    ("consigned", "10. Đã ký gửi"),
)
