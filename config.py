import logging
from datetime import datetime

# Настройка логирования
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f"logs/app_{timestamp}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)