from __future__ import annotations

import base64
from dataclasses import dataclass, field

import bcrypt
from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

# all of application's entity, use same registry to declarate
from funlab.flaskr.app import APP_ENTITIES_REGISTRY as entities_registry

def load_user(id_email, sa_session:Session)->UserEntity:
    stmt = select(UserEntity).where(or_(UserEntity.id == id_email
                                        , UserEntity.email == id_email, ))
    return sa_session.execute(stmt).scalar()

def save_user(user:UserEntity, sa_session:Session):
    sa_session.merge(user)
    sa_session.commit()

@dataclass
class User:
    id:int = field(init=False)
    email:str  # this what we use to login, not username
    username:str  # just a name
    password:str
    avatar_url:str
    state:str # = field(init=False)
    is_admin:bool =  field(init=False)
    role: str = field(init=False)

    def __post_init__(self):
        self.is_admin = False
        if getattr(self, 'password', None) is None:
            self.password = 'account+is+from+external+authentication+provider!!!'
        self.hash_pass()

    def to_userentity(self, exist=False):
        user_entity = UserEntity(username=self.username, email=self.email,
                        password=self.password, avatar_url=self.avatar_url, state=self.state)
        if exist:
            user_entity.id = self.id
        user_entity.state = self.state
        user_entity.is_admin = self.is_admin
        return user_entity

    @property
    def is_active(self):
        return self.state=='active'

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return self.role.upper() == 'GUEST'

    def get_id(self):
        return str(self.id)

    # ref:https://www.vitoshacademy.com/hashing-passwords-in-python/
    def hash_pass(self):
        def is_hashed() -> bool:
            try:
                hashed = base64.b64decode(self.password.encode()).decode()
                if len(hashed) == 60 and hashed[:4] in ["$2b$", "$2a$", "$2y$"]:
                    return True
            except:
                return False
            return False
        """Hash a password for storing."""
        if not is_hashed():
            hashed = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt())
            self.password = base64.b64encode(hashed).decode()
        return self.password

    def verify_pass(self, provided_password:str):
        """Verify a stored password against one provided by user"""
        hashed = base64.b64decode(self.password.encode())
        result = bcrypt.checkpw(provided_password.encode(), hashed)
        return result

@dataclass
class OAuthUser(User):
    def __post_init__(self):
        super().__post_init__()

    @property
    def external_attrs(self):
        return ['username', 'email', 'avatar_url']

@entities_registry.mapped
@dataclass
class UserEntity(User):
    __tablename__ = 'user'
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer, primary_key=True, autoincrement=True)})  # id = db.Column(GUID(), primary_key=True
    username: str = field(metadata={'sa': Column(String, nullable=False)})
    email: str = field(metadata={'sa': Column(String, nullable=False, unique=True, index=True)})
    password: str = field(metadata={'sa': Column(String, nullable=False)})
    avatar_url:str = field(metadata={'sa': Column(String)})
    state:str = field(metadata={'sa': Column(String)})
    is_admin:bool = field(init=False, metadata={'sa': Column(Boolean)})
    role: str = field(init=False, metadata={'sa': Column(String)})

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "role",
    }

    __table_args__ = (UniqueConstraint('email', name='_user_email_uc'),)

    def merge_userdata(self, oauth_user:OAuthUser):
        updated=False
        for attr in vars(oauth_user):
            if attr in oauth_user.external_attrs:
                if hasattr(self, attr) and getattr(self, attr)!=getattr(oauth_user, attr):
                    setattr(self, attr, getattr(oauth_user, attr))  # user update google
                    updated=True
        return updated

