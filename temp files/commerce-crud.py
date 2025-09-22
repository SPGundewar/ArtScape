from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from typing import List, Optional

# Wishlist operations
def add_to_wishlist(db: Session, user_id: int, artwork_id: int):
    """Add artwork to user's wishlist"""
    try:
        db_item = models.WishlistItem(user_id=user_id, artwork_id=artwork_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        return None  # Already in wishlist

def remove_from_wishlist(db: Session, user_id: int, artwork_id: int):
    """Remove artwork from user's wishlist"""
    db_item = db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id == user_id,
        models.WishlistItem.artwork_id == artwork_id
    ).first()
    
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def get_user_wishlist(db: Session, user_id: int):
    """Get user's wishlist"""
    return db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id == user_id
    ).all()

def is_in_wishlist(db: Session, user_id: int, artwork_id: int):
    """Check if artwork is in user's wishlist"""
    return db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id == user_id,
        models.WishlistItem.artwork_id == artwork_id
    ).first() is not None

# Order operations
def create_order(db: Session, order: schemas.OrderCreate, buyer_id: int, artist_id: int, amount: float):
    """Create a new order"""
    db_order = models.Order(
        buyer_id=buyer_id,
        artwork_id=order.artwork_id,
        artist_id=artist_id,
        amount=amount,
        shipping_address=order.shipping_address,
        payment_method=order.payment_method
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    """Get order by ID"""
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_user_orders(db: Session, user_id: int):
    """Get all orders for a user"""
    return db.query(models.Order).filter(models.Order.buyer_id == user_id).all()

def update_order_status(db: Session, order_id: int, status: models.OrderStatus):
    """Update order status"""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order