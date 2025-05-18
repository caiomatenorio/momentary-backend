from dataclasses import dataclass

from .session_data import SessionData


@dataclass
class JwtPayload:
    data: SessionData
    exp: int
    iat: int

    def to_dict(self) -> dict:
        return {
            "data": self.data.to_dict(),
            "exp": self.exp,
            "iat": self.iat,
        }

    @staticmethod
    def from_dict(data: dict) -> "JwtPayload":
        return JwtPayload(
            data=SessionData.from_dict(data["data"]),
            exp=data["exp"],
            iat=data["iat"],
        )
