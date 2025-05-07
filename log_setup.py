import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Loglama yapılandırması
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RotatingFileHandler("app.log", maxBytes=5 * 1024 * 1024, backupCount=3),
            logging.StreamHandler()
        ]
    )

    # Redis ve diğer kütüphaneler için log seviyesini uyarı olarak ayarla
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    # Ana logger'ı döndür
    return logging.getLogger(__name__)
