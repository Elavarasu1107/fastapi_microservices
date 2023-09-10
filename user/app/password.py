from passlib.hash import pbkdf2_sha256


def set_password(raw_password):
    return pbkdf2_sha256.hash(raw_password)


def check_password(user, raw_password):
    return pbkdf2_sha256.verify(raw_password, user.password)
