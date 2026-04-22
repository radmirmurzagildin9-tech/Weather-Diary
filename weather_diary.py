import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x500")
        
        self.data_file = "data/weather_data.json"
        self.entries = []
        self.load_data()
        
        self.create_widgets()
        self.update_table()
    
    def create_widgets(self):
        # Frame для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поля ввода
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        self.precip_var = tk.BooleanVar()
        self.precip_check = ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        self.precip_check.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="Добавить запись", command=self.add_entry)
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Frame для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по температуре (>):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=10, pady=5)
        
        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Таблица для отображения записей
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки сохранения/загрузки
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_btn = ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_json)
        self.save_btn.pack(side="left", padx=5)
        
        self.load_btn = ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_json)
        self.load_btn.pack(side="left", padx=5)
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_temperature(self, temp_str):
        try:
            float(temp_str)
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        if not self.validate_temperature(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return
        
        entry = {
            "date": date,
            "temperature": float(temp),
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        
        self.entries.append(entry)
        self.update_table()
        
        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        messagebox.showinfo("Успех", "Запись добавлена!")
    
    def update_table(self, filtered_entries=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = filtered_entries if filtered_entries is not None else self.entries
        
        for entry in data:
            self.tree.insert("", "end", values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                entry["precipitation"]
            ))
    
    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()
        
        filtered = self.entries.copy()
        
        if filter_date:
            filtered = [e for e in filtered if e["date"] == filter_date]
        
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
                filtered = [e for e in filtered if e["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура для фильтра должна быть числом")
                return
        
        self.update_table(filtered)
    
    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
    
    def save_to_json(self):
        os.makedirs("data", exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успех", f"Данные сохранены в {self.data_file}")
    
    def load_from_json(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            self.update_table()
            messagebox.showinfo("Успех", f"Данные загружены из {self.data_file}")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл с данными не найден")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Ошибка чтения JSON файла")
    
    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.entries = []


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
