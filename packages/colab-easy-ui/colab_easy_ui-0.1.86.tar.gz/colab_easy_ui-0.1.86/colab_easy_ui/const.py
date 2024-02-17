def is_running_on_colab():
    try:
        import google.colab  # NOQA

        return True
    except ImportError:
        return False


def sanitaize_path(path: str) -> bool:
    if path.startswith(".") or path.startswith("/"):
        return False
    return True
