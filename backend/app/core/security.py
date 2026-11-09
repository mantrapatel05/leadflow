import hashlib
import hmac


def verify_meta_signature(
    payload: bytes,
    signature: str | None,
    app_secret: str,
) -> bool:
    if not signature or not app_secret:
        return False
    expected_signature = "sha256=" + hmac.new(
        app_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)