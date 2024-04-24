class ErrorCode:
    AUTHENTICATION_REQUIRED = "Authentication required."
    AUTHORIZATION_FAILED = "Authorization failed. User has no access."
    INVALID_TOKEN = "Invalid token."
    INVALID_CREDENTIALS = "Invalid credentials."
    EMAIL_TAKEN = "Email is already taken."
    INVALID_PASSWORD = ("Password must contain at least "
                        "one lower character, "
                        "one upper character, "
                        "digit or "
                        "special symbol")
