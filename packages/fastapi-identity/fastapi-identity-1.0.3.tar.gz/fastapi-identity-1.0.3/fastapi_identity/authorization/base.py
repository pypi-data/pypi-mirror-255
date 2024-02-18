from abc import abstractmethod

from fastapi_identity.authorization.handler_context import AuthorizationHandlerContext


class AuthorizationHandler:
    @abstractmethod
    async def handle(self, context: AuthorizationHandlerContext):
        pass


class AuthorizationPolicy:
    def __init__(self, requirements: list[AuthorizationHandler]):
        self.requirements: list[AuthorizationHandler] = requirements or []
