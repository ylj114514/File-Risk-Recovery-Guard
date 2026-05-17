"""Flask application factory and web entry point."""

from __future__ import annotations

from flask import Flask

from ..config import DEFAULT_HOST, DEFAULT_PORT
from ..utils import setup_logging
from .routes import bp


def create_app() -> Flask:
    """
    创建 Flask 应用。
    注册页面路由和 API 路由。
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.register_blueprint(bp)
    return app


def main() -> None:
    """
    Web 服务入口。
    默认监听 127.0.0.1:5000。
    """
    setup_logging()
    app = create_app()
    print("[OK] File-Risk-Recovery-Guard Web Console started.")
    print(f"URL: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
