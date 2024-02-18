class SignInResult:
    def __init__(self, succeeded: bool = False, is_locked_out: bool = False):
        self._succeeded = succeeded
        self._is_locked_out = is_locked_out

    @property
    def is_locked_out(self):
        return self._is_locked_out

    @property
    def succeeded(self):
        return self._succeeded

    @staticmethod
    def success():
        return SignInResult(succeeded=True)

    @staticmethod
    def locked_out():
        return SignInResult(is_locked_out=True)

    @staticmethod
    def failed():
        return SignInResult()

    def __str__(self):
        if self._is_locked_out:
            return "Locked out"
        if self._succeeded:
            return "Succeeded"
        return "Failed"
