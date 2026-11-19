from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.price import calculate_selling_price
from app.modules.address.repository import AddressRepository
from app.modules.cart.repository import CartRepository
from app.modules.order.model import Order, OrderItem
from app.modules.order.repository import OrderRepository
from app.modules.order.schemas import (
    OrderRead,
    OrderStatus,
    OrderStatusUpdate,
    PaymentStatus,
    PlaceOrderRequest,
)
from app.modules.products.repository import ProductRepository
from app.modules.users.model import User
from app.modules.users.schemas import UserRole


class OrderService:
    def __init__(self, db: Session):
        self.addressRepository = AddressRepository(db)
        self.cartRepository = CartRepository(db)
        self.orderRepository = OrderRepository(db)
        self.productRepository = ProductRepository(db)

    def _dump_order(self, order: Order) -> OrderRead:
        items = self.orderRepository.get_items_by_order_id(order.id)

        order_read = OrderRead(
            id=order.id,
            user_id=order.user_id,
            shipping_address_id=order.shipping_address_id,
            total_items=order.total_items,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            items=items,
        )

        return order_read

    def place_order(self, current_user: User, payload: PlaceOrderRequest) -> OrderRead:
        # get the selectd address

        shipping_address = self.addressRepository.get_by_id(payload.shipping_address_id)

        # if address exist and belongd to current_user
        if shipping_address is None or shipping_address.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="shipping address not found",
            )

        # get users cart
        cart = self.cartRepository.get_active_cart_by_user_id(current_user.id)
        # check if cart exist
        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="shopping cart not found"
            )

        cart_items = self.cartRepository.get_items_by_cart_id(cart.id)

        order_items: list[OrderItem] = []
        total_items = 0
        total_amount = 0

        for cart_item in cart_items:
            product = self.productRepository.get_by_id(cart_item.product_id)

            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="product not active"
                )

            if cart_item.quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock for product",
                )

            unit_selling_price = calculate_selling_price(
                product.price, product.discount_percent
            )

            subtotal = unit_selling_price * cart_item.quantity
            total_amount += subtotal
            total_items += cart_item.quantity
            product.stock_quantity -= cart_item.quantity

            order_item = OrderItem(
                order_id=0,
                product_id=product.id,
                product_name=product.name,
                product_image_url=product.image_url,
                quantity=cart_item.quantity,
                unit_price=product.price,
                unit_selling_price=unit_selling_price,
                subtotal=subtotal,
            )

            order_items.append(order_item)

        order = Order(
            user_id=current_user.id,
            shipping_address_id=payload.shipping_address_id,
            total_items=total_items,
            total_amount=total_amount,
            status=OrderStatus.PENDING.value,
            payment_status=PaymentStatus.PENDING.value,
        )

        db_order = self.orderRepository.place_order(order, order_items, cart_items)

        return self._dump_order(db_order)

    def list_my_order(self, current_user: User) -> list[OrderRead]:
        orders = self.orderRepository.get_by_user_id(current_user.id)
        return [self._dump_order(order) for order in orders]

    def list_all_orders(self, current_user: User) -> list[OrderRead]:
        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied"
            )
        orders = self.orderRepository.get_all()
        return [self._dump_order(order) for order in orders]

    def get_order(self, order_id: int, current_user: User) -> OrderRead:
        order = self.orderRepository.get_by_id(order_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="order not found"
            )

        if (
            current_user.role != UserRole.ADMIN.value
            and order.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied"
            )

        return self._dump_order(order)

        # user 1 => admin  => access
        # user 2 => customer => not access
        # user 3 => customer => access

    def update_order_status(
        self, current_user: User, order_id: int, payload: OrderStatusUpdate
    ) -> OrderRead:

        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied"
            )

        order = self.orderRepository.get_by_id(order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="order not found"
            )

        order.status = payload.status.value
        db_order = self.orderRepository.update(order)
        return self._dump_order(db_order)
