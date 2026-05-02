import hashlib


def image_url_to_filename(url) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()
