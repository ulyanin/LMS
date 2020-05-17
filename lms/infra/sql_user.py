# pylint: disable=abstract-method

from typing import Iterable, Dict, Optional, Tuple
from abc import ABCMeta

from lms.domain.user import User, UpdateResult
import lms.infra.db.postgres_executor as pe


class SqlUser(User, metaclass=ABCMeta):
    @staticmethod
    async def login(*, email: str, password: str) -> Optional[str]:
        query = """
        SELECT user_id
        FROM users
        WHERE email = $1 and hashed_password = crypt($2, hashed_password)"""
        resolved_user_id = await pe.fetch_val(
            query=query,
            params=(email, password)
        )
        return resolved_user_id

    @staticmethod
    async def update_email_password(
            *,
            user_id,
            email,
            password: str,
    ) -> bool:
        query = """
        UPDATE users
        SET (email, hashed_password) = ROW($2, crypt($3, gen_salt('bf')))
        WHERE user_id=$1
        RETURNING user_id
        """
        returned_user_id = await pe.fetch_val(
            query=query,
            params=(user_id, email, password)
        )
        return returned_user_id is not None

    @staticmethod
    async def register(*, verification_code: str, email: str, password: str) -> Tuple[bool, str]:
        query = "SELECT user_id, hashed_password FROM users WHERE verification_code = $1"
        user_record = await pe.fetch_row(
            query=query,
            params=(verification_code,)
        )
        resolved_user_id = user_record.get('user_id')
        maybe_password = user_record.get('hashed_password')
        if not resolved_user_id:
            return False, 'invalid verification code'
        if maybe_password:
            return False, 'already registered'
        print('register', resolved_user_id, email, password)
        result = await SqlUser.update_email_password(
            user_id=resolved_user_id,
            email=email,
            password=password
        )
        assert result
        return True, 'successfully registered'

    @staticmethod
    async def check_is_professor(*, user_id: int) -> bool:
        query = "SELECT user_id FROM professors WHERE user_id = $1"
        resolved_user_id = await pe.fetch_val(
            query=query,
            params=(user_id,)
        )
        return resolved_user_id is not None

    async def get_info(
            self,
            *,
            properties: Optional[Iterable[str]] = None
    ):
        if properties is None:
            properties = self.properties()
        if not properties:
            return {}
        query = """SELECT * FROM users WHERE user_id=$1"""
        user_record = await pe.fetch_row(
            query=query,
            params=(self.user_id,)
        )
        if user_record is None:
            return None
        user = {}
        allowed_properties = self.properties()
        for param in properties:
            if param in allowed_properties:
                user[param] = user_record.get(param, None)
        return user

    async def update_info(
            self,
            *,
            update: Dict
    ) -> UpdateResult:
        assert self.authenticated
        for key in update:
            if key not in self.editable_properties():
                return UpdateResult(
                    success=False,
                    msg=f'error: field "{key}" is not editable',
                )
        fields = list(update.keys() & self.editable_properties())
        fields_str = ", ".join(fields)
        fields_values = tuple([update[field] for field in fields])
        values_placeholders = ", ".join([f"${i + 2}" for i in range(len(fields))])
        query = f"""
        UPDATE users 
        SET ({fields_str}) = ROW({values_placeholders}) 
        WHERE user_id=$1 
        RETURNING user_id """
        updated_user_id = await pe.fetch_val(
            query=query,
            params=(self.user_id,) + fields_values)
        if updated_user_id:
            return UpdateResult(success=True)
        return UpdateResult(success=False, msg='unknown error')
