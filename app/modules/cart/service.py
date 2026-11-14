
from fastapi import HTTPException, status

from app.common.price import calculate_selling_price
from app.modules.cart.model import Cart, CartItem
from app.modules.cart.repository import CartRepository
from app.modules.cart.schemas import (
  AddCartItemRequest,
  CardProductSummary,
  CartItemRead,
  CartRead,
  UpdateCartItemRequest,
)
from app.modules.products.repository import ProductRepository
from app.modules.users.model import User


class CartService:
  def __init__(self, db) -> None:
    self.cart_repository = CartRepository(db)
    self.product_repository = ProductRepository(db)

  def _build_cart_response(self, user_id: int, cart: Cart | None):

    if cart is None:
      return CartRead(
        id=None,
        user_id=user_id.id,
        total_items=0,
        total_amount=0,
        is_active=True,
        items=[]
      )
    cart_items = self.cart_repository.get_items_by_cart_id(cart.id)
    
    serialized_items: list[CartItem] = []
    total_items = 0.0
    total_amount = 0.0

    for item in cart_items:
      product = self.product_repository.get_by_id(item.product_id)

      if product is None:
        continue

      selling_price = calculate_selling_price(product.price, product.discount_percent)
      subtotal = round(selling_price * item.quantity, 2)

      cart_item_read = CartItemRead(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=product.price,
        unit_selling_price=selling_price,
        subtotal=subtotal,
        product=CardProductSummary(
          id=product.id,
          name=product.name,
          discount_percent=product.discount_percent,
          price=product.price,
          selling_price=selling_price,
          image_url=product.image_url
        )
      )
      serialized_items.append(cart_item_read)
      total_items += item.quantity
      total_amount += subtotal
    
    return CartRead(
      id=cart.id,
      user_id=cart.user_id,
      total_items=total_items,
      total_amount=total_amount,
      is_active=cart.is_active,
      items=serialized_items
    )
  
  def _get_or_create_active_cart(self, user_id: int) -> Cart:
    cart = self.cart_repository.get_active_cart_by_user_id(user_id)
    if cart is not None:
      return cart
    
    return self.cart_repository.create_cart(
      Cart(user_id=user_id, is_active=True)
    )

  def _validate_product_for_cart(self, product_id: int):
    product = self.product_repository.get_by_id(product_id)

    if product is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found in database")
    
    if not product.is_active:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="product is not active")

    return product

  def get_my_cart(self, current_user: User) -> CartRead:
    cart= self.cart_repository.get_active_cart_by_user_id(current_user.id)

    cart_read = self._build_cart_response(current_user.id, cart)
    return cart_read
  
  def add_items(self, current_user:User, payload: AddCartItemRequest) -> CartRead:

    product_id = payload.product_id 

    # check product is exist in datavbase and is actve
    product = self._validate_product_for_cart(product_id)

    
    #fetch or create users cart
    cart = self._get_or_create_active_cart(current_user.id)

    # is product already exist in cart
    existing_item = self.cart_repository.get_item_by_cart_and_product(
      cart.id, product_id
    )

    new_qauntity = payload.quantity
    
    if existing_item is not None:
      new_qauntity += existing_item.quantity
    
    if new_qauntity > product.stock_quantity:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"not enugh stock for product : {product.name}"
      )
    
    if existing_item is not None:
      existing_item.quantity = new_qauntity
      self.cart_repository.update__item(existing_item)
    else:
      self.cart_repository.create_item(
        CartItem(
          cart_id=cart.id,
          product_id=product.id,
          quantity=new_qauntity
        )  
      )

    # rebuild and return cart response
    return self._build_cart_response(current_user.id, cart)
      
    
  def update_item(self, current_user: User, item_id: int, payload: UpdateCartItemRequest) -> CartRead:
    cart = self.cart_repository.get_active_cart_by_user_id(current_user.id)

    if cart is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cart not found")

    item = self.cart_repository.get_item_by_id(item_id)
    if item is None or item.cart_id != cart.id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    
    product = self._validate_product_for_cart(item.product_id)

    if payload.quantity > product.stock_quantity:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"not enugh stock for product : {product.name}"
      )
    
    item.quantity = payload.quantity
    self.cart_repository.update__item(item)

    return self._build_cart_response(current_user.id, cart)

    
  def remove_item(self, current_user: User, item_id: int) -> CartRead:
    cart = self.cart_repository.get_active_cart_by_user_id(current_user.id)
    if cart is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cart not found")
    
    item = self.cart_repository.get_item_by_id(item_id)
    if item is None or item.cart_id != cart.id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")

    self.cart_repository.delete__item(item)

    cart_items = self.cart_repository.get_items_by_cart_id(cart.id)
    if not cart_items:
      cart.is_active = False
      self.cart_repository.db.commit()

    return self._build_cart_response(current_user.id, cart)

  
  def clear_cart(self, current_user: User) -> CartRead:
    cart = self.cart_repository.get_active_cart_by_user_id(current_user.id)
    if cart is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cart not found")

    self.cart_repository.clear_items(cart.id)
    cart.is_active = False
    self.cart_repository.db.commit()

    return self._build_cart_response(current_user.id, cart)
    

    
    
  
    
    
    

    
      

      

    
    


