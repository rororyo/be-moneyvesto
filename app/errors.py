class AppError(Exception):
    """Base class for custom exceptions."""
    pass

class UserAlreadyExistsError(AppError):
    pass

class UserNotFoundError(AppError):
    pass

class InvalidRoleError(AppError):
    pass

# You can define errors for other domains too (e.g., AuthError, CourseError, etc.)
