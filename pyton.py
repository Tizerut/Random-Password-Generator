import random
import string
import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Файл истории
        self.history_file = "history.json"
        self.history = self.load_history()

        # Создание виджетов
        self.create_widgets()
        self.update_password()

    def create_widgets(self):
        # Рамка для параметров
        frame = LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        frame.pack(pady=10, padx=10, fill="x")

        # Длина пароля
        Label(frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_var = IntVar(value=12)
        self.length_scale = Scale(frame, from_=4, to=32, orient=HORIZONTAL,
                                  variable=self.length_var, length=300)
        self.length_scale.grid(row=0, column=1, padx=10)
        self.length_label = Label(frame, text="12")
        self.length_label.grid(row=0, column=2)
        self.length_scale.config(command=lambda x: self.length_label.config(text=str(self.length_var.get())))

        # Чекбоксы
        self.use_digits = BooleanVar(value=True)
        self.use_letters = BooleanVar(value=True)
        self.use_punctuation = BooleanVar(value=False)

        Checkbutton(frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        Checkbutton(frame, text="Буквы (A-Z a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        Checkbutton(frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_punctuation).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = Button(frame, text="Сгенерировать пароль", command=self.update_password,
                                   bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле для пароля
        self.password_var = StringVar()
        self.password_entry = Entry(self.root, textvariable=self.password_var, font=("Courier", 14),
                                    justify="center", state="readonly")
        self.password_entry.pack(pady=10, padx=10, fill="x")

        # Кнопка копирования
        self.copy_btn = Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        Label(self.root, text="История паролей:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        
        # Фрейм для таблицы и скролла
        history_frame = Frame(self.root)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = Scrollbar(history_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.tree = ttk.Treeview(history_frame, columns=("Password", "Length", "Date"), show="headings",
                                 yscrollcommand=scrollbar.set)
        self.tree.heading("Password", text="Пароль")
        self.tree.heading("Length", text="Длина")
        self.tree.heading("Date", text="Дата и время")
        self.tree.column("Password", width=300)
        self.tree.column("Length", width=80)
        self.tree.column("Date", width=150)
        self.tree.pack(side=LEFT, fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Кнопка очистки истории
        self.clear_btn = Button(self.root, text="Очистить историю", command=self.clear_history,
                                bg="#f44336", fg="white")
        self.clear_btn.pack(pady=5)

        # Загрузка истории в таблицу
        self.refresh_history_table()

    def generate_password(self):
        length = self.length_var.get()
        
        # Проверка корректности длины
        if length < 4:
            messagebox.showwarning("Ошибка", "Минимальная длина пароля — 4 символа")
            self.length_var.set(4)
            self.length_scale.set(4)
            self.length_label.config(text="4")
            length = 4
        elif length > 32:
            messagebox.showwarning("Ошибка", "Максимальная длина пароля — 32 символа")
            self.length_var.set(32)
            self.length_scale.set(32)
            self.length_label.config(text="32")
            length = 32
        
        # Проверка, что выбран хотя бы один тип символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_punctuation.get()):
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов")
            return None
        
        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_punctuation.get():
            chars += "!@#$%^&*"
        
        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))
        return password

    def update_password(self):
        password = self.generate_password()
        if password:
            self.password_var.set(password)
            self.save_to_history(password)

    def save_to_history(self, password):
        from datetime import datetime
        entry = {
            "password": password,
            "length": len(password),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self.save_history()
        self.refresh_history_table()

    def refresh_history_table(self):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Заполнение заново
        for entry in self.history[-20:]:  # Показываем последние 20 паролей
            self.tree.insert("", END, values=(entry["password"], entry["length"], entry["date"]))

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Ошибка", "Нет пароля для копирования")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()
            messagebox.showinfo("Готово", "История очищена")

if __name__ == "__main__":
    root = Tk()
    app = PasswordGenerator(root)
    root.mainloop()