"""CLI tool: đăng nhập TCBS và lưu token.

Sử dụng::

    vnstock-tcbs-login

hoặc::

    python -m vnstock.cli.tcbs_login

Quy trình:
  1. Nhập tên đăng nhập và mật khẩu (ẩn khi nhập).
  2. Gửi yêu cầu đăng nhập tới TCBS.
  3. Nếu TCBS yêu cầu OTP → nhập mã 6 chữ số từ ứng dụng TCInvest.
  4. Token được lưu vào ~/.config/vnstock/tcbs_token.json.

Token có thể được sử dụng bởi tất cả TCBS provider classes.
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

# ── minimal import — do NOT import all of vnstock at startup ──────────────
from vnstock.explorer.tcbs.auth import TCBSAuth, TCBSAuthError, TCBSOTPRequired


def _print(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    """Entry point for the ``vnstock-tcbs-login`` CLI command.

    Returns exit code (0 = success, 1 = failure).
    """
    _print("=" * 60)
    _print("  vnstock — Đăng nhập TCBS")
    _print("=" * 60)
    _print("Token sẽ được lưu tại: ~/.config/vnstock/tcbs_token.json")
    _print("Đặt biến môi trường TCBS_BEARER_TOKEN để bỏ qua bước này.")
    _print("")

    # ── credentials ──────────────────────────────────────────────────────
    try:
        username = input("Tên đăng nhập TCBS (VD: 105C123456): ").strip()
        if not username:
            _print("[LỖI] Tên đăng nhập không được để trống.")
            return 1

        password = getpass.getpass("Mật khẩu: ")
        if not password:
            _print("[LỖI] Mật khẩu không được để trống.")
            return 1
    except (KeyboardInterrupt, EOFError):
        _print("\n[HỦY] Đăng nhập bị hủy.")
        return 1

    auth = TCBSAuth()

    # ── step 1: credentials ───────────────────────────────────────────────
    otp_session: str | None = None
    try:
        _print("\nĐang xác thực...")
        token = auth.login(username=username, password=password)
        _print("[OK] Đăng nhập thành công (không cần OTP).")

    except TCBSOTPRequired as e:
        otp_session = e.otp_session
        _print("[INFO] TCBS yêu cầu mã OTP.")

    except TCBSAuthError as e:
        _print(f"\n[LỖI] Đăng nhập thất bại:\n  {e}")
        return 1

    # ── step 2: OTP (if required) ─────────────────────────────────────────
    if otp_session is not None:
        try:
            otp = input("Nhập mã OTP 6 chữ số từ ứng dụng TCInvest: ").strip()
            if not otp or len(otp) != 6 or not otp.isdigit():
                _print("[LỖI] Mã OTP phải gồm đúng 6 chữ số.")
                return 1
        except (KeyboardInterrupt, EOFError):
            _print("\n[HỦY] Đăng nhập bị hủy.")
            return 1

        try:
            _print("\nĐang xác thực OTP...")
            token = auth.confirm_otp(otp_session=otp_session, otp=otp)
            _print("[OK] Xác thực OTP thành công.")
        except TCBSAuthError as e:
            _print(f"\n[LỖI] Xác thực OTP thất bại:\n  {e}")
            return 1

    # ── save token ────────────────────────────────────────────────────────
    try:
        saved_path: Path = TCBSAuth.save_token(token=token)
        _print(f"\n[OK] Token đã lưu tại: {saved_path}")
    except OSError as e:
        _print(f"\n[CẢNH BÁO] Không thể lưu token: {e}")
        _print(f"  Token: {token}")
        _print("  Hãy đặt TCBS_BEARER_TOKEN=<token> trong biến môi trường.")

    _print("")
    _print("Bây giờ bạn có thể sử dụng TCBS provider:")
    _print("  from vnstock.explorer.tcbs import Quote")
    _print("  q = Quote(symbol='FPT')  # tự động tải token")
    _print("  df = q.history(start='2024-01-01', end='2024-12-31', interval='1D')")
    _print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
