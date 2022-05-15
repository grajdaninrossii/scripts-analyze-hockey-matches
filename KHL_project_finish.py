# Программа, анализирующая статистику игр КХЛ
# Командное задание группы 1

import pandas as pd
import random
import time
import sys

# Загрузка всех данных о прошедших матчах из csv-файла в зависимости от сезона
def load_cvs_file():
    global season
    season = input("Введите название сезона (например 2013_14): ") # Ввод названия сезона
    name_file ="./khl_" + season + ".csv" # Конструирование пути к сsv файлу
    try: # обработка исключения, если файл не будет найден
        source_data = pd.read_csv(name_file, delimiter = ',') # Исходные данные из csv-файла(создание датафрейма)
    except Exception:
        print("Ошибка ввода названия сезона!\nЗавершение работы программы")
        sys.exit(0) # Завершение работы программы
    source_data = source_data.drop(["Unnamed: 0", "Номер", "Дата"], axis = 1) # Удаление лишних столбцов из исходной таблицы
    return source_data

# Составления таблицы
def create_table(csv_path):
    teams = pd.unique(csv_path[["Команда_1", "Команда_2"]].values.ravel()) # Заполнение списка команд уникальными значениями
    new_table = []
    for x in teams:
        y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        y.insert(0, x)
        new_table.append(y)
    return new_table

# Изменения списка, в счетах за периоды
def string_modification(string):
    modification_list = [] # Создаем новый список для перезаписи
    for i in range(len(string)): # Запись изменных элементов в новый список
        elem = string[i].split(":")
        if elem[0] == '': # Проверка элементов и при необходимости их редактирование
            elem[0] = 0
            elem[1] = 0
        elif len(elem) == 2:
            elem[0] = int(elem[0])
            elem[1] = int(elem[1])
        else:
            elem = elem[0]
        modification_list.append(elem) # Заполнение нового списка
    modification_list.append(modification_list[3]) # изменение расположения элементов списка
    modification_list.append(modification_list[0])
    modification_list.pop(0)
    modification_list.pop(2)
    return modification_list

# Расчет показатателей для двух команд и запись их двумерный массив
def get_score_of_game(s):
    goals_team1 = 0
    goals_team2 = 0
    counter = 0
    while counter < 3 or (goals_team1 == goals_team2 and counter >= 3): # получаем список общего счета и фиксируем в когда закончилась игра
        goals_team1 += s[counter + 2][0]
        goals_team2 += s[counter + 2][1]
        counter +=1 # фиксируем когда закончилась игра(3 - осн. время, 4 - овертайм, 5 - буллиты)
    data = [goals_team1, goals_team2]
    finish_list = [[s[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [s[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # Узнаем как кто победил, кто проиграл и заносим в список + добавляем очки
    hi = 1 # Вспомогательная переменная(обратная i)
    for i in range(2): # Подсчет шайб, очков, типов побед и поражений
        if data[i] > data[hi]: # Проверка победы одной команды над другой(проверяет каждую из двух команд)
            if counter == 3: # Если игра закончилось в основное время
                finish_list[i][1] += 1 # В i-ой команде
                finish_list[i][7] += 3 # О i-ой команде
                finish_list[hi][6] += 1 # П hi-ой команде
            elif counter == 4: # Если игра закончилась в овертайме
                finish_list[i][2] += 1 # ВО i-ой команде
                finish_list[i][7] += 2 # О i-ой команде
                finish_list[hi][5] += 1 # ПО hi-ой команде
                finish_list[hi][7] += 1 # О hi-ой команде
            else: # Если игра закончилась в серии буллитов
                finish_list[i][3] += 1 # ВБ i-ой команде
                finish_list[i][7] += 2 # О i-ой команде
                finish_list[hi][4] += 1 # ПБ hi-ой команде
                finish_list[hi][7] += 1 # О hi-ой команде
        finish_list[i][9] += data[i] # Добавляем кол-во заброшенных шайб
        finish_list[i][10] += data[hi] # Добавляем кол-во пропущенных шайб
        hi -= 1
        finish_list[i][8] += finish_list[i][9] - finish_list[i][10] # Считаем и добавляем разницу шайб
    return finish_list

# Заплнение столбцов в таблице
def create_finish_table(array_info, new):# на вход: [['Динамо Мн', 1, 0, 0, 0, 0, 0, 3, 2, 2, 0], ['Автомобилист', 0, 0, 0, 0, 0, 1, 0, -2, 0, 2]]
    for i in range(2):
        n = 0
        while new[n][0] != array_info[i][0]:
            n += 1
        for x in range(len(new[0])-1):
            new[n][x+1] += array_info[i][x+1]
    return new

# Функция перевода столбцов "ЗШ" и "ПШ" в столбец "Ш" вида "ЗШ-ПШ"(через тире)
def score_counter():
    cut_table = finish_table[["ЗШ", "ПШ"]] # Берем два столбца: "ЗШ" и "ПШ"
    new_column = []
    for i in range(len(cut_table)):
        list_1 = cut_table.loc[i].tolist()
        new_column.append(str(list_1[0]) + "-" + str(list_1[1]))
    finish_table.insert(7, "Ш", new_column)

# Добавление к общей таблице столбца "И"
def game_counter(): # Считаем количство игр для одной из команд
    n = len(csv_path[csv_path["Команда_1"] == csv_path.loc[0, "Команда_1"]]) + len(csv_path[csv_path["Команда_2"] == csv_path.loc[0, "Команда_1"]])
    finish_table.insert(1, "И", list) # Создаем столбец(список датафрейм)
    finish_table[["И"]] = n # и прираниваем его элементы к количеству сыгранных игр

# Функция редактирования конечной таблицы
def sort_table():
    global finish_table
    finish_table = finish_table.sort_values(by = ["О", "В", "ВО", "ВБ", "РШ", "ЗШ"], ascending = False).reset_index(drop = True) # Сортировка и переиндексация таблицы
    for i in range(len(finish_table) - 1):# Проходимся по всем строкам в поиске абсолютно одинаковых команд (процесс жеребьевки)
        if (finish_table.drop(["Клуб"], axis = 1).loc[i] == finish_table.drop(["Клуб"], axis = 1).loc[i + 1]).all(): # Если строки абсолютно равны
            random_num = int(random.random()*2) # Переменная, которая будет равна либо 0 либо 1
            if random_num == 0: # Оставляем как и было
                pass
            else: # Меняем местами друг с другом команды, у которых все показатели одинаковы
                team2 = finish_table.loc[i+1].tolist()
                finish_table.loc[i+1] = finish_table.loc[i]
                finish_table.loc[i] = team2
    finish_table = finish_table.drop(["РШ","ЗШ","ПШ"], axis = 1).reset_index(drop = True) # Удаление разницы шайб и забитых шайб и переиндексация после замены одинаковых команд

#Главная функция
def main_function():
    global csv_path, finish_table
    csv_path = load_cvs_file() # Вводим название сезона
    start_time = time.time() # Время
    new_table = create_table(csv_path) # Создание таблицы(со значением 0)
    for i in range(len(csv_path)): # Цикл, в котором будут происходить все вычисления и результаты сохранятся в finish_table(сначала в виде списка в new)
        string = csv_path.loc[i].tolist() # Присваивание переменной string строки датафрейма и перевод его в список
        string = string_modification(string) # Изменения списка, в счетах за периоды
        array_info = get_score_of_game(string) # Присваивание переменной один список с результатами матчей для двух команд
        new = create_finish_table(array_info, new_table) # Фунцкия редактирования конечной таблицы
    finish_table = pd.DataFrame(new, columns = ["Клуб", "В", "ВО", "ВБ", "ПБ", "ПО", "П", "О", "РШ", "ЗШ", "ПШ"])
    score_counter() # Функция перевода столбцов "ЗШ" и "ПШ" в столбец "Ш" вида "ЗШ-ПШ"(через тире)
    game_counter() # Функция счета количество сыгранных игр и добавление их столбцом в конечную таблицу
    sort_table() # Сортировка таблицы по убыванию
    print(finish_table)
    print("--- %s seconds ---" % (time.time() - start_time)) # Скорость программы



#-----------------------------------------------------------------------НАЧАЛО РАБОТЫ ПРОГРАММЫ-------------------------------------------------------------
main_function()