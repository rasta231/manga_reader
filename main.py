import os
import tkinter as tk
from tkinter import ttk
import sqlite3
import io

import requests
from tkinter import messagebox
from function import count_man, count_girl, coun_records, update_table, delete_all_rows, \
    validate_int, validate_str
from PIL import ImageTk, Image
from io import BytesIO


#
#
def found_photo(event):
    item = tree.item(tree.focus())
    values = item['values']
    con = sqlite3.connect('game.db')
    cur = con.cursor()
    cur.execute("SELECT photo FROM gamers WHERE user_id = (SELECT user_id FROM gamers WHERE name = ?)", (values[1],))

    result = cur.fetchone()
    try:
        new_window = tk.Toplevel(root)
        image_data = result[0]
        image = ImageTk.PhotoImage(Image.open(io.BytesIO(image_data)))
        image_label = tk.Label(new_window, image=image)
        image_label.pack()
        image_label.image = image
    except IOError as e:
        messagebox.showerror("Ошибка ввода-вывода:", str(e))
    except Exception as e:
        messagebox.showerror("Произошла ошибка:", str(e))


def create_db():
    con = sqlite3.connect('game.db')
    cur = con.cursor()
    table_create = '''CREATE TABLE IF NOT EXISTS gamers (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            last_name TEXT,
            sex TEXT,
            age INTEGER,
            score INTEGER,
            photo_url VARCHAR,
            photo BLOB)'''
    con.execute(table_create)
    con.commit()
    con.close()


def press_found_photo(event):
    item = tree.item(tree.focus())
    values = item['values']
    new_window = tk.Toplevel(root)
    con = sqlite3.connect('game.db')
    cur = con.cursor()
    cur.execute("SELECT photo_url FROM gamers WHERE user_id = (SELECT user_id FROM gamers WHERE name = ?)",
                (values[1],))
    result = cur.fetchone()
    lab = tk.Label(new_window)
    lab.pack()

    if result is not None and result[0]:
        response = requests.get(result[0])
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            width, height = 300, 300  # Замените значения на желаемые размеры
            resized_image = image.resize((width, height))
            photo = ImageTk.PhotoImage(resized_image)
            lab.config(image=photo)
            lab.image = photo
        else:
            lab['text'] = 'Ошибка загрузки изображения'
    else:
        lab['text'] = 'URL изображения не найден'


def press_found():
    def found_on_name():
        con = sqlite3.connect('game.db')
        cur = con.cursor()
        if combo_change.get() == 'названию':
            cur.execute(f'SELECT * FROM gamers WHERE name == ?', (entry_found.get(),))
            ans = cur.fetchall()
            con.close()
            new_window.destroy()
            messagebox.showinfo('результат', *ans)

    new_window = tk.Toplevel(root)
    new_window.title(combo_change.get())
    frame_for_query = tk.Frame(new_window)
    frame_for_query.grid(row=0, column=0, padx=15, pady=15)

    label_found = tk.Label(frame_for_query, text=f'поиск по {combo_change.get()}')
    label_found.grid(row=0, column=0, pady=15, padx=15)

    button_found = tk.Button(new_window, text='Ok', command=found_on_name)
    button_found.grid(row=1, column=0, sticky='news')

    entry_found = tk.Entry(frame_for_query)
    entry_found.grid(row=0, column=1, pady=15, padx=15)


def update_counter_label():
    count = coun_records()
    counter_label.config(text=f'количество записей: {count}')


def show_query():
    con = sqlite3.connect('game.db')
    cur = con.cursor()
    number = combo_query.get()
    new_window = tk.Toplevel(root)
    new_window.title(combo_query.get())
    new_window.transient(root)  # Сделать новое окно модальным
    new_window.geometry("+%d+%d" % ((root.winfo_screenwidth() - new_window.winfo_reqwidth()) // 2,
                                    (root.winfo_screenheight() - new_window.winfo_reqheight()) // 2))
    new_window.update_idletasks()
    main_frame = tk.Frame(new_window)
    main_frame.pack()
    up_frame = tk.Frame(main_frame)

    up_frame.grid(row=0, column=0, sticky='w', pady=15, padx=15)
    down_frame = tk.LabelFrame(main_frame, text='результат')
    down_frame.grid(row=1, column=0, sticky='w', pady=15, padx=15)
    if combo_query.get() == 'Стаутс манги Читаю':
        cont_lb = tk.Label(down_frame, text=f'количество {combo_query.get().split(" ")[-1]}: {count_girl()}')
        cont_lb.grid(row=0, column=0, sticky='w', pady=15, padx=15)
        tree_sex = ttk.Treeview(up_frame, columns=('Название', 'Глава'), show='headings')
        tree_sex.heading('Название', text='Название')
        tree_sex.heading('Глава', text='Глава')
        tree_sex.pack()
        cur.execute("SELECT name, score FROM gamers WHERE sex = ?", ('Читаю',))
        rows = cur.fetchall()
        for item in tree_sex.get_children():
            tree_sex.delete(item)
        for row in rows:
            tree_sex.insert('', 'end', values=row)


    elif combo_query.get() == 'Стаутс манги Прочитал':
        cont_lb = tk.Label(down_frame, text=f'{combo_query.get().split(" ")[-1]}: {count_man()}')
        cont_lb.grid(row=0, column=0, sticky='w', pady=15, padx=15)
        tree_sex = ttk.Treeview(up_frame, columns=('Название', 'Глава'), show='headings')
        tree_sex.heading('Название', text='Название')
        tree_sex.heading('Глава', text='Глава')
        tree_sex.pack()
        cur.execute("SELECT name, score FROM gamers WHERE sex = ?", ('Прочитал',))
        rows = cur.fetchall()
        for item in tree_sex.get_children():
            tree_sex.delete(item)
        for row in rows:
            tree_sex.insert('', 'end', values=row)


def delete_row():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror('Ошибка', 'Пожалуйста, выберите строку для удаления')
        return

    values = tree.item(selected_item)['values']

    if len(values) < 5:
        messagebox.showerror('Ошибка', 'Недостаточное количество значений')
        return

    id, name, last_name, sex, age = values[:5]

    con = sqlite3.connect('game.db')
    cur = con.cursor()
    cur.execute("DELETE FROM gamers WHERE name=? AND last_name=? AND sex=? AND age=?",
                (name, last_name, sex, age))
    con.commit()
    con.close()

    press_update_table()
    update_counter_label()

    press_update_table()
    update_counter_label()


def press_update_table():
    for item in tree.get_children():
        tree.delete(item)

    for row in update_table():
        tree.insert('', 'end', values=row)


def press_delete_all_rows():
    delete_all_rows()
    update_counter_label()


def enter_button():
    con = sqlite3.connect('game.db')
    cur = con.cursor()
    names = name_ent.get()
    fam = fam_ent.get()
    sex = combo_sex.get()
    age = age_spin.get()
    score = score_entry.get()
    url_photo = image_entry.get()
    if names == '' or fam == '' or sex == '' or age == '' or score == '':
        messagebox.showerror('Ошибка', 'Пожалуйста, заполните все поля')
        return
    cur.execute("SELECT * FROM gamers WHERE name=? AND last_name=? AND sex=? AND age=?",
                (names, fam, sex, age))
    existing_row = cur.fetchone()
    if existing_row:
        messagebox.showerror('Ошибка', 'Запись уже существует в базе данных')
        con.close()
        return
    ins_que = '''INSERT INTO gamers (name, last_name, sex, age, score, photo_url) VALUES (?,?,?,?,?,?)'''
    ins_tup = (names, fam, sex, age, score, url_photo)
    cur.execute(ins_que, ins_tup)
    con.commit()
    con.close()
    update_counter_label()


create_db()
root = tk.Tk()

frame = tk.Frame(root)
frame.pack()

validate_int_cmd = root.register(validate_int)
validate_str_cmd = root.register(validate_str)

up_frame = tk.Frame(frame)
up_frame.grid(row=0, column=0, sticky='w', pady=15, padx=15)

# Фрэйм для ввода данных
info_frame = tk.LabelFrame(up_frame, text='Ввод данных')
info_frame.grid(row=0, column=0, padx=15, pady=15, sticky='s')

name = tk.Label(info_frame, text='Название')
name.grid(row=0, column=0)

family = tk.Label(info_frame, text='Тип')
family.grid(row=0, column=1)

name_ent = tk.Entry(info_frame, validate='key', validatecommand=(validate_str_cmd, '%P'))
fam_ent = ttk.Combobox(info_frame, values=['Манхва', 'Манга', 'Аниме'])
fam_ent.current(0)
name_ent.grid(row=1, column=0)
fam_ent.grid(row=1, column=1)

titlee = tk.Label(info_frame, text='Статус')
combo_sex = ttk.Combobox(info_frame, values=['Читаю', 'Прочитал', 'Заброшено', 'В планах', 'Смотрю'], state='readonly')
combo_sex.current(0)
combo_sex.grid(row=1, column=2)
titlee.grid(row=0, column=2)

age_label = tk.Label(info_frame, text='Год выхода')
age_spin = tk.Spinbox(info_frame, validate='key', validatecommand=(validate_int_cmd, '%P'), from_=2000, to=2023, )
age_spin.grid(row=3, column=0)
age_label.grid(row=2, column=0)

score_label = tk.Label(info_frame, text='глава на данный момент')
score_entry = tk.Entry(info_frame, validate='key', validatecommand=(validate_int_cmd, '%P'))
score_label.grid(row=2, column=1)
score_entry.grid(row=3, column=1)

image_label = tk.Label(info_frame, text='фото')
image_entry = tk.Entry(info_frame)
image_label.grid(row=2, column=2)
image_entry.grid(row=3, column=2)

for i in info_frame.winfo_children():
    i.grid_configure(padx=10, pady=5)

# Рамка для кнопок
but_frame = tk.LabelFrame(up_frame, text="Кнопки")
but_frame.grid(row=0, column=1, sticky='news', pady=15, padx=15)

but = tk.Button(but_frame, text='Добавить', command=enter_button)
but.grid(row=0, column=0, pady=10, padx=15, sticky='news', )

but1 = tk.Button(but_frame, text='Обновить таблицу', command=press_update_table)
but1.grid(row=0, column=1, pady=10, padx=15, sticky='news')

but2 = tk.Button(but_frame, text='Удалить', command=delete_row)
but2.grid(row=1, column=0, pady=10, padx=15, sticky='news')

but3 = tk.Button(but_frame, text='Удалить все записи', command=press_delete_all_rows)
but3.grid(row=1, column=1, pady=10, padx=15, sticky='news')

# but4 = tk.Button(but_frame, text='Добавить 10 записей', command=press_add_10)
# but4.grid(row=2, column=0, pady=10, padx=15, sticky='news')

query_name = ['Стаутс манги Читаю', 'Стаутс манги Прочитал']
combo_query = ttk.Combobox(but_frame, values=query_name, state='readonly', width=25)
combo_query.current(1)
combo_query.grid(row=0, column=3, pady=10, padx=15, sticky='news')

but5 = tk.Button(but_frame, text='Запросы', command=show_query)
but5.grid(row=1, column=3, pady=10, padx=15, sticky='news')

combo_change = ttk.Combobox(but_frame, values=['названию'], state='readonly')
combo_change.current(0)
combo_change.grid(row=0, column=4, pady=10, padx=15, sticky='news')
but6 = tk.Button(but_frame, text='Поиск по критерию', command=press_found)
but6.grid(row=1, column=4, pady=10, padx=15, sticky='news')

# Фрэйм для таблицы со всеми записями
table_frame = tk.Frame(frame)
table_frame.grid(row=1, column=0, padx=15, pady=15)
col = ('id', 'Название', 'Тип', 'Статус', 'Год выхода', 'глава на данный момент')
tree = ttk.Treeview(table_frame, columns=col, show='headings', style="Custom.Treeview")
style = ttk.Style()
style.configure("Treeview", font=("TkDefaultFont", 12))

tree.tag_configure("Custom.Treeview", font=('Arial', 12))
tree.column('id', anchor='center')
tree.column('Название', anchor='center')
tree.column('Тип', anchor='center')
tree.column('Статус', anchor='center')
tree.column('Год выхода', anchor='center')
tree.column('глава на данный момент', anchor='center')

tree.heading('id', text='id')
tree.heading('Название', text='Название')
tree.heading('Тип', text='Количество глав')
tree.heading('Статус', text='Статус')
tree.heading('Год выхода', text='Год выхода')
tree.heading('глава на данный момент', text='глава на данный момент')
tree.grid(row=0, column=0, padx=15, pady=15)

counter_label = tk.Label(root, text=f'количество записей: {coun_records()}')
counter_label.pack(anchor='w', padx=15, pady=15)
# Создание скроллбара
scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
tree.configure(yscrollcommand=scrollbar.set)
tree.bind("<Double-1>", press_found_photo)

root.mainloop()
