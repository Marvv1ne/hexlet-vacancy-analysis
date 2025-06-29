from telegram import ReplyKeyboardMarkup

# Удаляем неиспользуемые переменные
# keyboard_settings = [
#     ['create_settings', 'update_settings'],
#     ['Done'],
# ]

# Настройка фильтра
# keyboard_filters = [
#     ['frontend', 'backend'],
# ]

# keyboard_front = [
#     ['Angular', 'React', 'JS'],
#     ['HTML', 'CSS', 'Vue.js'],
#     ['set interval'],
# ]

# keyboard_backend = [
#     ['Java', 'Nodejs', 'Go'],
#     ['Python', 'PHP', 'C++'],
#     ['set interval'],
# ]

# Настройка интервала
# keyboard_interval = [
#     ['Day', 'Week', 'Month'],
#     ['set format'],
# ]

# Настройка формата выгрузки
# keyboard_format = [
#     ['PDF', 'Excel'],
#     ['Done'],
# ]

# Актуальные клавиатуры, соответствующие регулярным выражениям в fsm.py
markup_filters = ReplyKeyboardMarkup([["frontend", "backend"], ["🔙 Назад"]], resize_keyboard=True)
markup_front = ReplyKeyboardMarkup([["React", "Vue.js", "Angular"], ["JS", "HTML", "CSS"], ["Готово", "Отменить выбор", "🔙 Назад"]], resize_keyboard=True)
markup_backend = ReplyKeyboardMarkup([["Python", "Java", "Nodejs"], ["Go", "PHP", "C++"], ["Готово", "Отменить выбор", "🔙 Назад"]], resize_keyboard=True)
markup_interval = ReplyKeyboardMarkup([["minute", "day", "week"], ["🔙 Назад"]], resize_keyboard=True)
markup_format = ReplyKeyboardMarkup([["PDF", "Excel"], ["🔙 Назад"]], resize_keyboard=True)
markup_settings = ReplyKeyboardMarkup([
    ["create_settings"],
    ["update_settings"],
    ["delete_settings"],
    ["🔙 Назад"]
], resize_keyboard=True)



