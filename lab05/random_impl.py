from congen import MLCG
import logging

def get_binary_answer(generator, p: float = 0.5):
    """Возвращает ДА или НЕТ с вероятностью p"""
    logging.warning(generator.random())
    return "ДА" if generator.random() < p else "НЕТ"

class MagicBall:
    def __init__(self, answers=None):
        if answers is None:
            self.answers = ["Да", "Абсолютно точно", "Не могу сказать",
                            "Нет", "Безусловно", "Ответ Нет",
                            "Вряд ли", "Похоже, что да", "Без сомнений",
                            "Должно быть так", "Звезды говорят: Да!", "Мало шансов",
                            "Ответ не ясен", "Спросите позже", "Спросите снова",
                            "Очень вероятно", "Мне кажется да", "Духи говорят Да", 
                            "Звезды против", "Потряси меня еще"]
        else:
            self.answers = answers
        self.prob = 1.0 / len(self.answers)
        self.generator = MLCG(89)

    def get_answer(self):
        """Возвращает случайный ответ из списка."""
        alpha = self.generator.random()
        cumulative = 0.0
        for answer in self.answers:
            cumulative += self.prob
            if alpha < cumulative:
                return answer
        return self.answers[-1]