"""
User CRUD 작업 (간소화)
"""
from sqlalchemy.orm import Session
from database.models.user import User
from typing import List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
now = lambda: datetime.now(timezone.utc)


def create_user(
    db: Session,
    username: str,
    email: str
) -> User:
    """
    사용자 생성
    
    Args:
        db: DB 세션
        username: 사용자명
        email: 이메일
    
    Returns:
        생성된 User 객체
    """
    try:
        user = User(
            username=username,
            email=email,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"✅ User created: {username}")
        return user
    except Exception as e:
        logger.error(f"❌ Failed to create user: {e}")
        db.rollback()
        raise


def get_user(db: Session, username: str) -> Optional[User]:
    """사용자 조회 (username)"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """사용자 조회 (ID)"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """사용자 조회 (email)"""
    return db.query(User).filter(User.email == email).first()


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    only_active: bool = True
) -> List[User]:
    """
    사용자 목록 조회
    
    Args:
        db: DB 세션
        skip: 건너뛸 개수
        limit: 최대 개수
        only_active: 활성 사용자만 조회
    
    Returns:
        User 리스트
    """
    query = db.query(User)
    
    if only_active:
        query = query.filter(User.is_active == True)
    
    return query.order_by(User.username).offset(skip).limit(limit).all()


def update_user(
    db: Session,
    username: str,
    **kwargs
) -> Optional[User]:
    """
    사용자 업데이트
    
    Args:
        db: DB 세션
        username: 사용자명
        **kwargs: 업데이트할 필드들
    
    Returns:
        업데이트된 User 객체
    """
    try:
        user = get_user(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        logger.info(f"✅ User updated: {username}")
        return user
    except Exception as e:
        logger.error(f"❌ Failed to update user: {e}")
        db.rollback()
        raise


def delete_user(db: Session, username: str) -> bool:
    """
    사용자 삭제
    
    Args:
        db: DB 세션
        username: 사용자명
    
    Returns:
        성공 여부
    """
    try:
        user = get_user(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            return False
        
        db.delete(user)
        db.commit()
        logger.info(f"✅ User deleted: {username}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete user: {e}")
        db.rollback()
        raise
