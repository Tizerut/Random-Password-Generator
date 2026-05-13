import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # Файл данных
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()

        # Категории
        self.categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные услуги", 
                          "Здоровье", "Одежда", "Образование", "Другое"]

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table_frame()
        self.create_stats_frame()

        # Загрузка данных в таблицу
        self.refresh_table()

    def create_input_frame(self):
        """Форма для добавления расходов"""
        input_frame = tk.LabelFrame(self.root, text="Добавление расхода", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Сумма
        tk.Label(input_frame, text="Сумма (₽):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=self.categories, width=15, state="readonly")
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = tk.Entry(input_frame, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="Добавить расход", command=self.add_expense,
                                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

    def create_filter_frame(self):
        """Фильтрация данных"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(pady=5, padx=10, fill="x")

        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        categories_filter = ["Все"] + self.categories
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                   values=categories_filter, width=15, state="readonly")
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по дате (период)
        tk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_from_var = tk.StringVar()
        self.filter_date_from_entry = tk.Entry(filter_frame, textvariable=self.filter_date_from_var, width=12)
        self.filter_date_from_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="до (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_to_var = tk.StringVar()
        self.filter_date_to_entry = tk.Entry(filter_frame, textvariable=self.filter_date_to_var, width=12)
        self.filter_date_to_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка применения фильтра
        self.apply_filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter,
                                          bg="#2196F3", fg="white")
        self.apply_filter_btn.grid(row=0, column=6, padx=10, pady=5)

        # Кнопка сброса фильтра
        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить", command=self.reset_filter,
                                          bg="#FF9800", fg="white")
        self.reset_filter_btn.grid(row=0, column=7, padx=5, pady=5)

    def create_table_frame(self):
        """Таблица с расходами"""
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Скроллбар
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Таблица
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Date", "Category", "Amount"), 
                                 show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("ID", text="№")
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Category", text="Категория")
        self.tree.heading("Amount", text="Сумма (₽)")
        self.tree.column("ID", width=40)
        self.tree.column("Date", width=100)
        self.tree.column("Category", width=120)
        self.tree.column("Amount", width=100)
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Кнопка удаления
        self.delete_btn = tk.Button(self.root, text="Удалить выбранную запись", command=self.delete_expense,
                                    bg="#f44336", fg="white")
        self.delete_btn.pack(pady=5)

    def create_stats_frame(self):
        """Статистика и сумма за период"""
        stats_frame = tk.LabelFrame(self.root, text="Статистика", padx=10, pady=10)
        stats_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(stats_frame, text="Общая сумма за выбранный период:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        self.total_sum_var = tk.StringVar(value="0 ₽")
        self.total_sum_label = tk.Label(stats_frame, textvariable=self.total_sum_var, 
                                        font=("Arial", 14, "bold"), fg="#4CAF50")
        self.total_sum_label.pack(side=tk.LEFT, padx=10)

    def add_expense(self):
        """Добавление расхода"""
        # Проверка суммы
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректную сумму (число)!")
            return

        # Проверка даты
        date_str = self.date_var.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2026-05-15)")
            return

        category = self.category_var.get()

        # Создание записи
        expense = {
            "id": len(self.expenses) + 1 if self.expenses else 1,
            "date": date_str,
            "category": category,
            "amount": amount
        }

        self.expenses.append(expense)
        self.save_expenses()
        self.refresh_table()
        
        # Очистка поля суммы
        self.amount_var.set("")
        
        messagebox.showinfo("Успех", f"Расход {amount} ₽ на категорию '{category}' добавлен!")

    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
            # Получаем ID из таблицы
            item = self.tree.item(selected[0])
            expense_id = item['values'][0]
            
            # Удаляем из списка
            self.expenses = [e for e in self.expenses if e['id'] != expense_id]
            
            # Перенумерация ID
            for idx, expense in enumerate(self.expenses, 1):
                expense['id'] = idx
            
            self.save_expenses()
            self.refresh_table()
            messagebox.showinfo("Успех", "Расход удалён!")

    def get_filtered_expenses(self):
        """Получение отфильтрованных расходов"""
        filtered = self.expenses.copy()

        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e['category'] == category_filter]

        # Фильтр по дате (от)
        date_from = self.filter_date_from_var.get().strip()
        if date_from:
            try:
                datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [e for e in filtered if e['date'] >= date_from]
            except ValueError:
                pass

        # Фильтр по дате (до)
        date_to = self.filter_date_to_var.get().strip()
        if date_to:
            try:
                datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [e for e in filtered if e['date'] <= date_to]
            except ValueError:
                pass

        return filtered

    def refresh_table(self):
        """Обновление таблицы и подсчёт суммы"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получение отфильтрованных данных
        filtered_expenses = self.get_filtered_expenses()

        # Заполнение таблицы
        for expense in filtered_expenses:
            self.tree.insert("", tk.END, values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ))

        # Подсчёт суммы
        total = sum(e['amount'] for e in filtered_expenses)
        self.total_sum_var.set(f"{total:.2f} ₽")

    def apply_filter(self):
        """Применение фильтра"""
        # Проверка корректности дат
        date_from = self.filter_date_from_var.get().strip()
        date_to = self.filter_date_to_var.get().strip()

        if date_from:
            try:
                datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Ошибка", "Неверный формат даты 'от'!")
                return

        if date_to:
            try:
                datetime.strptime(date_to, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Ошибка", "Неверный формат даты 'до'!")
                return

        if date_from and date_to and date_from > date_to:
            messagebox.showwarning("Ошибка", "Дата 'от' не может быть позже даты 'до'!")
            return

        self.refresh_table()

    def reset_filter(self):
        """Сброс фильтра"""
        self.filter_category_var.set("Все")
        self.filter_date_from_var.set("")
        self.filter_date_to_var.set("")
        self.refresh_table()

    def load_expenses(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_expenses(self):
        """Сохранение данных в JSON"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
