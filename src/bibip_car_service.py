from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
import os
from decimal import Decimal
from datetime import datetime
from collections import defaultdict



class CarService:
    REC_LEN = 500
    REC_FULL = REC_LEN + 1
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    def _get_number_rows(self, file_name: str) -> int:
        path: str = os.path.join(self.root_directory_path, file_name)

        if not os.path.exists(path):
            return 0
        count: int = 0

        with open(path, 'r', encoding='utf-8') as f:
            for _ in f:
                count += 1
            return count

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        line_count: int = self._get_number_rows("models.txt")
        new_id: int = line_count + 1

        model_line: str = f"{new_id};{model.name};{model.brand}".ljust(self.REC_LEN)
        with open(os.path.join(self.root_directory_path, "models.txt"), "a", encoding="utf-8") as f:
            f.write(model_line + "\n")

        index_line = f"{new_id};{line_count}".ljust(self.REC_LEN)
        with open(os.path.join(self.root_directory_path, "models_index.txt"), "a", encoding="utf-8") as f:
            f.write(index_line + "\n")

        return Model(id=new_id, name=model.name, brand=model.brand)

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        line_count: int = self._get_number_rows("cars.txt")

        date_str = car.date_start.strftime('%Y-%m-%d')

        car_line = f"{car.vin};{car.model};{car.price:.2f};{date_str};{car.status}".ljust(self.REC_LEN)

        with open(os.path.join(self.root_directory_path, "cars.txt"), "a", encoding="utf-8") as f:
            f.write(car_line + "\n")

        index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index_lines = f.readlines()
        else:
            index_lines = []

        new_index_line = f"{car.vin};{line_count}\n"
        index_lines.append(new_index_line)

        index_lines.sort(key=lambda line: line.split(";")[0])

        with open(index_path, "w", encoding="utf-8") as f:
            for line in index_lines:
                f.write(line.strip().ljust(self.REC_LEN) + "\n")
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(index_path, "r", encoding="utf-8") as f:
            index_lines = f.readlines()

        car_line_number = None
        for line in index_lines:
            vin_in_file, line_no = line.strip().split(";")
            if vin_in_file == sale.car_vin:
                car_line_number = int(line_no)
                break

        if car_line_number is None:
            raise ValueError(f"VIN {sale.car_vin} not found in cars_index.txt")

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r+", encoding="utf-8") as f:
            f.seek(car_line_number * self.REC_FULL)
            raw_line = f.read(self.REC_LEN)

            parts = raw_line.strip().split(";")
            vin, model_id, price, date_start_str, status = parts
            parts[4] = "sold"

            new_line = ";".join(parts).ljust(self.REC_LEN)
            f.seek(car_line_number * self.REC_FULL)
            f.write(new_line)

        sale_line_number = self._get_number_rows("sales.txt")
        sale_id = sale.sales_number

        sale_date = sale.sales_date.strftime("%Y-%m-%d")
        sale_line = f"{sale_id};{sale.car_vin};{float(sale.cost):.2f};{sale_date}".ljust(self.REC_LEN)

        with open(os.path.join(self.root_directory_path, "sales.txt"), "a", encoding="utf-8") as f:
            f.write(sale_line + "\n")

        index_path = os.path.join(self.root_directory_path, "sales_index.txt")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                sales_index = f.readlines()
        else:
            sales_index = []

        new_sales_index_line = f"{sale_id};{sale_line_number}\n"
        sales_index.append(new_sales_index_line)
        sales_index.sort(key=lambda line: line.split(";")[0])

        with open(index_path, "w", encoding="utf-8") as f:
            for line in sales_index:
                f.write(line.strip().ljust(self.REC_LEN) + "\n")

        return Car(
            vin=vin,
            model=int(model_id),
            price=float(price),
            date_start=datetime.strptime(date_start_str, "%Y-%m-%d"),
            status="sold"
        )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        result = []

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        if not os.path.exists(cars_path):
            return []

        with open(cars_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) < 5:
                    continue

                vin, model_id, price, date_start_str, car_status = parts
                if car_status != status.value:
                    continue

                car = Car(
                    vin=vin,
                    model=int(model_id),
                    price=Decimal(price),
                    date_start=datetime.strptime(date_start_str, "%Y-%m-%d"),
                    status=CarStatus(car_status)
                )
                result.append(car)

        return result

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        with open(os.path.join(self.root_directory_path, "cars_index.txt"), "r", encoding="utf-8") as f:
            for line in f:
                vin_index, line_no = line.strip().split(";")
                if vin_index == vin:
                    car_line_no = int(line_no)
                    break
            else:
                return None

        with open(os.path.join(self.root_directory_path, "cars.txt"), "r", encoding="utf-8") as f:
            f.seek(car_line_no * self.REC_FULL)
            raw_car = f.read(self.REC_LEN)

        vin, model_id, price, date_start_str, status = raw_car.strip().split(";")
        model_id = int(model_id)
        price = Decimal(price)
        date_start = datetime.strptime(date_start_str, "%Y-%m-%d")
        status = CarStatus(status)

        with open(os.path.join(self.root_directory_path, "models_index.txt"), "r", encoding="utf-8") as f:
            for line in f:
                mid, line_no = line.strip().split(";")
                if int(mid) == model_id:
                    model_line_no = int(line_no)
                    break
            else:
                return None

        with open(os.path.join(self.root_directory_path, "models.txt"), "r", encoding="utf-8") as f:
            f.seek(model_line_no * self.REC_FULL)
            raw_model = f.read(self.REC_LEN)

        _, model_name, model_brand = raw_model.strip().split(";")

        sales_date = None
        sales_cost = None
        sale_path = os.path.join(self.root_directory_path, "sales.txt")
        if os.path.exists(sale_path):
            with open(sale_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) < 4:
                        continue
                    _, sale_vin, cost, sale_date_str = parts
                    if sale_vin == vin:
                        sales_cost = Decimal(cost)
                        sales_date = datetime.strptime(sale_date_str, "%Y-%m-%d")
                        break

        return CarFullInfo(
            vin=vin,
            car_model_name=model_name,
            car_model_brand=model_brand,
            price=price,
            date_start=date_start,
            status=status,
            sales_date=sales_date,
            sales_cost=sales_cost,
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(index_path, "r", encoding="utf-8") as f:
            index_lines = f.readlines()

        index_data = []
        car_line_no = None

        for line in index_lines:
            vin_index, line_no = line.strip().split(";")
            if vin_index == vin:
                car_line_no = int(line_no)
            index_data.append([vin_index, int(line_no)])

        if car_line_no is None:
            raise ValueError(f"VIN {vin} not found")

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r+", encoding="utf-8") as f:
            f.seek(car_line_no * self.REC_FULL)
            raw_line = f.read(self.REC_LEN)

            parts = raw_line.strip().split(";")
            _, model_id, price, date_start_str, status = parts

            parts[0] = new_vin
            new_line = ";".join(parts).ljust(self.REC_LEN)

            f.seek(car_line_no * self.REC_FULL)
            f.write(new_line)

        for idx in index_data:
            if idx[0] == vin:
                idx[0] = new_vin
                break

        index_data.sort(key=lambda x: x[0])

        with open(index_path, "w", encoding="utf-8") as f:
            for vin_index, line_no in index_data:
                f.write(f"{vin_index};{line_no}".ljust(self.REC_LEN) + "\n")

        return Car(
            vin=new_vin,
            model=int(model_id),
            price=Decimal(price),
            date_start=datetime.strptime(date_start_str, "%Y-%m-%d"),
            status=CarStatus(status)
        )

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        index_path = os.path.join(self.root_directory_path, "sales_index.txt")
        with open(index_path, "r", encoding="utf-8") as f:
            index_lines = f.readlines()

        sale_line_no = None
        for line in index_lines:
            line = line.strip()
            if not line or line.startswith("is_deleted"):
                continue

            parts = [p.strip() for p in line.split(";") if p.strip()]
            if len(parts) < 2:
                continue

            sale_id, line_no_str = parts[:2]
            if sale_id == sales_number:
                sale_line_no = int(line_no_str)
                break

        if sale_line_no is None:
            raise ValueError(f"Sale {sales_number} not found in index")

        # 2. Прочитать строку из sales.txt
        sales_path = os.path.join(self.root_directory_path, "sales.txt")
        with open(sales_path, "r+", encoding="utf-8") as f:
            f.seek(sale_line_no * self.REC_FULL)
            raw_line = f.read(self.REC_LEN).strip()

        if raw_line.startswith("is_deleted"):
            raise ValueError("Sale already deleted")

        sale_parts = [p.strip() for p in raw_line.split(";")]
        if len(sale_parts) < 4:
            raise ValueError("Invalid sale record")

        _, vin, _, _ = sale_parts

        with open(sales_path, "r+", encoding="utf-8") as f:
            f.seek(sale_line_no * self.REC_FULL)
            f.write("is_deleted".ljust(self.REC_LEN) + "\n")

        car_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(car_index_path, "r", encoding="utf-8") as f:
            car_index_lines = f.readlines()

        car_line_no = None
        for line in car_index_lines:
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split(";")]
            if len(parts) != 2:
                continue

            vin_index, line_no_str = parts
            if vin_index == vin:
                car_line_no = int(line_no_str)
                break

        if car_line_no is None:
            raise ValueError("Car VIN not found in index")

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r+", encoding="utf-8") as f:
            f.seek(car_line_no * self.REC_FULL)
            raw_car = f.read(self.REC_LEN).strip()

            parts = raw_car.split(";")
            if len(parts) < 5:
                raise ValueError("Invalid car record")

            vin, model_id, price, date_start_str, _ = parts
            parts[4] = CarStatus.available.value
            updated_line = ";".join(parts).ljust(self.REC_LEN)

            f.seek(car_line_no * self.REC_FULL)
            f.write(updated_line + "\n")

        return Car(
            vin=vin,
            model=int(model_id),
            price=Decimal(price),
            date_start=datetime.strptime(date_start_str, "%Y-%m-%d"),
            status=CarStatus.available
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        model_sales: dict[int, int] = defaultdict(int)

        cars_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        cars_index = {}
        with open(cars_index_path, "r", encoding="utf-8") as f:
            for line in f:
                vin, line_no = line.strip().split(";")
                cars_index[vin] = int(line_no)

        sales_path = os.path.join(self.root_directory_path, "sales.txt")
        with open(sales_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("is_deleted"):
                    continue
                parts = line.strip().split(";")
                if len(parts) < 4:
                    continue
                _, vin, _, _ = parts
                line_no = cars_index.get(vin)
                if line_no is None:
                    continue

                cars_path = os.path.join(self.root_directory_path, "cars.txt")
                with open(cars_path, "r", encoding="utf-8") as car_file:
                    car_file.seek(line_no * self.REC_FULL)
                    car_line = car_file.read(self.REC_LEN).strip()
                    car_parts = car_line.split(";")
                    if len(car_parts) < 5:
                        continue
                    model_id = int(car_parts[1])
                    model_sales[model_id] += 1

        model_index_path = os.path.join(self.root_directory_path, "models_index.txt")
        model_line_map = {}
        with open(model_index_path, "r", encoding="utf-8") as f:
            for line in f:
                model_id, line_no = line.strip().split(";")
                model_line_map[int(model_id)] = int(line_no)

        models_path = os.path.join(self.root_directory_path, "models.txt")
        models_info = {}
        with open(models_path, "r", encoding="utf-8") as f:
            for model_id, line_no in model_line_map.items():
                f.seek(line_no * self.REC_FULL)
                model_line = f.read(self.REC_LEN).strip()
                parts = model_line.split(";")
                if len(parts) < 3:
                    continue
                _, name, brand = parts
                models_info[model_id] = (name, brand)

        result = []
        for model_id, count in model_sales.items():
            if model_id in models_info:
                name, brand = models_info[model_id]
                result.append(ModelSaleStats(
                    car_model_name=name,
                    brand=brand,
                    sales_number=count
                ))

        result.sort(key=lambda x: (-x.sales_number, x.car_model_name))

        return result[:3]
