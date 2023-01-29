from app.db.models import Role
from app.ops.user import create_user
from app import schemas
from fastapi.security import OAuth2PasswordRequestForm


TESTUSER_PASSWORD = "testuserxx"


class UserService:
    def __init__(self, db_session, service):
        self.db_session = db_session
        self.service = service
        self.id_counter = 0

    def new_user(self, *, name=None, role=Role.uploader, auth=False):
        self.id_counter += 1
        if name is None:
            name = f"user{self.id_counter}"

        user = create_user(
            self.db_session,
            schemas.UserCreate(name=name, password=TESTUSER_PASSWORD),
            role=role,
        )
        if not auth:
            return user

        response = self.service.login(
            data=OAuth2PasswordRequestForm(
                username=name, password=TESTUSER_PASSWORD, scope=""
            ),
            db=self.db_session,
        )
        token = response["access_token"]
        return user, {"Authorization": f"Bearer {token}"}
