from src.utils.logger_config import get_logger, log_exception

logger = get_logger("utils.interface")


class InterfaceUtils:
    """
    Утилиты для работы с интерфейсом.
    """

    @staticmethod
    @log_exception
    def estimate_text_width(text: str, font_size: int, avg_char_width: float = 0.6) -> int:
        """
        Вычисляет ширину текста в px.
        :param text: Текст
        :param font_size: Размер шрифта
        :param avg_char_width: Средняя ширина символа в "em" (для Arial примерно 0.6)
        :return: ширина текста в px
        """
        return int(len(text) * font_size * avg_char_width)
