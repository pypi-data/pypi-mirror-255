# custom exception types for this project
class PrefRefError(Exception):
  # base class
  pass

class PrefRefOptionMissingRequiredProperty(PrefRefError):
  def __init__(self, message, code: int = 569) -> None:
    self.message = message
    self.code = code
    super().__init__(f'{code}: {message}')

class PrefRefOptionNotFound(PrefRefError):
  def __init__(self, message, code: int = 569) -> None:
    self.message = message
    self.code = code
    super().__init__(f'{code}: {message}')

class PrefRefUnknownArgument(PrefRefError):
  def __init__(self, message, code: int = 569) -> None:
    self.message = message
    self.code = code
    super().__init__(f'{code}: {message}')

class PrefRefMissingRequiredOption(PrefRefError):
  def __init__(self, message, code: int = 569) -> None:
    self.message = message
    self.code = code
    super().__init__(f'{code}: {message}')
