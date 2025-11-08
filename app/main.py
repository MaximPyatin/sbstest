"""Точка входа для запуска API в режиме разработки с авто-перезапуском."""

import uvicorn


def main() -> None:
    """Запускает сервис API под управлением uvicorn в режиме разработки."""
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()


