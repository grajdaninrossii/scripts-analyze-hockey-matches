# Программа, анализирующая статистику игр КХЛ
# Индивидуальное задание 2(Кузин М.А)
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def load_cvs_file():
    global season, source_data, team_1, team_2
    season = input("Введите название сезона (например 2013_14): ") # Ввод названия сезона
    name_file ="khl_" + season + ".csv" # Конструирование пути к сsv файлу
    print(name_file)
    try: # обработка исключения, если файл не будет найден
        source_data = pd.read_csv(name_file, delimiter = ',') # Исходные данные из csv-файла(создание датафрейма)
    except Exception:
        print("Ошибка ввода названия сезона!\nЗавершение работы программы")
        sys.exit(0) # Завершение работы программы
    source_data = source_data.drop(["Unnamed: 0", "Номер", "Дата"], axis = 1) # Удаление лишних столбцов из исходной таблицы
    print("Введите интересующие вас команды")
    team_1 = input("Первую: ").strip()
    team_2 = input("Вторую: ").strip()
    teams = pd.unique(source_data[["Команда_1", "Команда_2"]].values.ravel()) # Загрузим список команд
    if team_1 not in teams: # Проверка правильности ввода
        print(f"Ошибка ввода! Нет {team_1} такой команды в этом сезоне")
        sys.exit(0)
    elif team_2 not in teams:
        print(f"Ошибка ввода! Нет {team_2} такой команды в этом сезоне")
        sys.exit(0)
    elif team_1 == team_2:
        print(f"Ошибка ввода! Вы ввели две одинаковые команды")
        sys.exit(0)

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
    modification_list.append(modification_list[3]) # Изменение расположения элементов списка
    modification_list.append(modification_list[0])
    modification_list.pop(0)
    modification_list.pop(2)
    return modification_list

# Расчет показатателей для двух команд и запись их двумерный массив
def get_score_of_game(s):
    global finish_list
    goals_team1 = 0
    goals_team2 = 0
    counter = 0
    while counter < 3 or (goals_team1 == goals_team2 and counter >= 3): # получаем список общего счета и фиксируем в когда закончилась игра
        goals_team1 += s[counter + 2][0]
        goals_team2 += s[counter + 2][1]
        counter +=1
    data = [goals_team1, goals_team2]
    finish_list = [[s[0], 0, 0], [s[1], 0, 0]]
    # Узнаем как кто победил, кто проиграл и заносим в список + добавляем очки
    if data[0] > data[1] and counter == 3:
        finish_list[0][2] += 3 # О 1-ой команде
    elif data[0] > data[1] and counter >= 4:
        finish_list[0][2] += 2 # О 1-ой команде
        finish_list[1][2] += 1 # О 2-ой команде
    elif data[0] < data[1] and counter == 3:
        finish_list[1][2] += 3 # О 2-ой команде
    else:
        finish_list[0][2] += 1 # О 1-ой команде
        finish_list[1][2] += 2 # О 2-ой команде
    return finish_list

# Заполняем списки полученными очками
def create_finish_table(array_info):
    for i in range(2): # Для двух команд
        if array_info[i][0] == team_1: # Если команда i == команде 1
            teams_score_and_games_1.append(teams_score_and_games_1[-1])
            teams_score_and_games_1[-1] += array_info[i][2]
        elif array_info[i][0] == team_2: # Если команда i == команде 2
            teams_score_and_games_2.append(teams_score_and_games_2[-1])
            teams_score_and_games_2[-1] += array_info[i][2]

# Основная функция работы программы
def main_function():
    global teams_score_and_games_1, teams_score_and_games_2
    load_cvs_file() # загрузка csv-файла
    teams_score_and_games_1 = [0] # Создаем списки для хранения рез-тов получения очков
    teams_score_and_games_2 = [0]
    for i in range(len(source_data)): # Цикл, в котором будут происходить все вычисления и результаты сохранятся в finish_table
        string = source_data.loc[i].tolist() # Присваивание переменной string строки датафрейма и перевод его в список
        string = string_modification(string) # Изменения списка, в счетах за периоды
        array_info = get_score_of_game(string) # Присваивание переменной один список с результатами матчей для двух команд
        create_finish_table(array_info) # Заполняем списки полученными очками
    teams_score_1 = np.array(teams_score_and_games_1) # Перевод списков с рез-ми наборов очков в список нампи
    teams_score_2 = np.array(teams_score_and_games_2)
    x = np.linspace(0, len(teams_score_1)-1, len(teams_score_1))
    plt.plot(x, teams_score_1, color = 'red', label = team_1) # График для первой команды
    plt.plot(x, teams_score_2,  color = 'blue', linestyle = '--', label = team_2) # График для второй команды
    plt.grid() # сетка
    # Подписи для осей:
    plt.xlabel('Кол-во сыгранных игр', fontsize = 14) # Подпись оси x
    plt.ylabel('Кол-во очков', fontsize = 14) # Посдпись оси y
    plt.ylim(0, 150) # Диапазон оси y
    plt.xlim(0, len(teams_score_1)) # Диапазон оси x
    plt.legend(loc = 'best') # Расположение легенды
    plt.title(f"Сравнение набранных очков от количества сыгранных игр для команд {team_1} и {team_2}", fontsize = 14, y = 1.05) # Заголовок
    plt.show()


#-----------------------------------------------------------------------НАЧАЛО РАБОТЫ ПРОГРАММЫ-------------------------------------------------------------
main_function()