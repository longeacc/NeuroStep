"""Email service — Phase 0 stub.

Logs the message instead of sending. Swap for a real provider (SMTP / Scaleway
Transactional Email / Postmark) in production without touching callers.
"""

import logging

logger = logging.getLogger("neurostep.email")


def send_verification_email(to: str, token: str) -> None:
    # In production this builds a link to the frontend, e.g.
    # https://app.neurostep.fr/verify?token=<token>
    logger.info("[email][verify] to=%s token=%s", to, token)
    print(f"[DEV EMAIL] Verify {to}: POST /api/v1/auth/verify-email?token={token}")
