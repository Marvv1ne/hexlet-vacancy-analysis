from telegram import ReplyKeyboardMarkup

markup_filters = ReplyKeyboardMarkup([
    ["frontend", "backend"],
    ["🔙 Назад"]
    ], resize_keyboard=True)

markup_front = ReplyKeyboardMarkup([
    ["React", "Vue.js", "Angular"],
    ["JS", "HTML", "CSS"],
    ["Готово", "Отменить выбор", "🔙 Назад"]
    ], resize_keyboard=True)

markup_backend = ReplyKeyboardMarkup([
    ["Python", "Java", "Nodejs"],
    ["Go", "PHP", "C++"],
    ["Готово", "Отменить выбор", "🔙 Назад"]
    ], resize_keyboard=True)

markup_interval = ReplyKeyboardMarkup([
    ["minute", "day", "week"],
    ["Отменить выбор", "🔙 Назад"]
    ], resize_keyboard=True)

markup_format = ReplyKeyboardMarkup([
    ["PDF", "Excel"],
    ["🔙 Назад"]
    ], resize_keyboard=True)

markup_settings = ReplyKeyboardMarkup([
    ["create_or_update_settings"],
    ["show_settings"],
    ["delete_settings"],
    ["exit"]
], resize_keyboard=True)
