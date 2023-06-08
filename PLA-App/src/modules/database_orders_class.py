import psycopg2


class Database():
    def __init__(self):
        # Initialize the database class with the connection parameters.

        self.dbname = "d42s9l8fg14nqm"
        self.user = "trroxnzyvifgnt"
        self.password = "85c17ff132d95b23eca8d735622ee140e9e09913e2dffd69586074c279217cba"
        self.host = "ec2-18-202-8-133.eu-west-1.compute.amazonaws.com"
        self.port = "5432"
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port)
        self.cur = self.conn.cursor()

        # Basic Modules to be used in subclasses

    def create_Table(self, table_name, columns):
        query = f"CREATE TABLE if not exists {table_name} ({columns});"
        self.cur.execute(query)
        self.conn.commit()

    def check_Amount(self, table_name, condition):
        query = f"SELECT COUNT (*)FROM {table_name} WHERE {condition}"
        self.cur.execute(query)
        self.conn.commit()
        result = self.cur.fetchone()
        return result[0] > 0

    def delete_Table(self, table_name):
        query = f"DROP TABLE {table_name} CASCADE;"
        self.cur.execute(query)
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

    def insert_Row(self, table_name, values):
        query = f"INSERT INTO {table_name} VALUES ({values});"
        self.cur.execute(query)
        self.conn.commit()

    def delete_Row(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()

    def update_Value(self, table_name, condition, new_values):
        query = f"UPDATE {table_name} SET {new_values} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
        return query

    def read_Values(self, table_name, variables, condition):
        query = f"SELECT {variables} FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchall()

    def read_Table(self, table_name):
        query = f"SELECT * FROM {table_name};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchall()

    def get_Max(self, table_name, column):
        query = f"SELECT MAX({column}) from {table_name}"
        self.cur.execute(query)
        result = self.cur.fetchone()[0]
        self.conn.commit()
        return (result)

    def read_Value(self, table_name, value, condition):
        query = f"SELECT {value} FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_column_values(self, table_name, column):
        query = f"SELECT {column} FROM {table_name};"
        self.cur.execute(query)
        self.conn.commit()
        column_values = [row[0] for row in self.cur.fetchall()]
        return column_values


class Concluded(Database):

    # # Concluded orders table subclass

    def check_Concluded(self, order):
        return self.check_Amount("concluded", f"number='{order}'")

    def add_Concluded(self, number, workpiece, quantity, duedate, latepen, earlypen, clientid):
        cl = Clients()
        if cl.check_Client(clientid) == True:
            self.insert_Row("concluded",
                            f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        else:
            cl.add_Client(clientid)
            self.insert_Row("concluded",
                            f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        cl.close()

    def delete_Concluded(self, number, clientid):
        self.delete_Row("concluded", f"number='{number}' AND clientid='{clientid}'")

    def update_Concluded(self, number, new_quantity):
        self.update_Value("concluded", f"number={number}", f"quantity={new_quantity}")

    def read_All_Concluded(self):
        col_names = ["number", "workpiece", "quantity", "duedate", "latepen", "earlypen", "clientid"]
        result_list = []
        rows = self.read_Table("concluded")
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)

        return result_list

    def read_Concluded_Number_X(self, order_number):
        col_names = ["number", "workpiece", "quantity", "duedate", "latepen", "earlypen", "clientid"]
        rows = self.read_Values("concluded", "number,workpiece,quantity,duedate,latepen,earlypen,clientid",
                                f"number={order_number}")
        result_list = []
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
        return result_list

    def read_X_Concluded(self, number_of_orders):
        col_names = ["number", "workpiece", "quantity", "duedate", "latepen", "earlypen", "clientid"]
        rows = self.read_Table("concluded")
        result_list = []
        a = 0
        for row in rows:
            if a == number_of_orders:
                break
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
            a = a + 1
        return result_list

    def Latest_Due_Date(self):
        Latest = self.get_Max("concluded", "duedate")
        return Latest


class Orders(Database):

    # Orders table subclass

    def check_Order(self, order):
        return self.check_Amount("orders", f"number='{order}'")

    def add_Order(self, number, workpiece, quantity, duedate, latepen, earlypen, clientid):
        cl = Clients()
        if cl.check_Client(clientid) == True:
            self.insert_Row("orders",
                            f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        else:
            cl.add_Client(clientid)
            self.insert_Row("orders",
                            f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        cl.close()

    def delete_Order(self, number, clientid):
        self.delete_Row("orders", f"number='{number}' AND clientid='{clientid}'")

    def update_Order(self, number, new_quantity):
        self.update_Value("orders", f"number={number}", f"quantity={new_quantity}")

    def read_All_Orders(self):
        col_names = ["number", "workpiece", "quantity", "duedate", "latepen", "earlypen", "clientid"]
        result_list = []
        rows = self.read_Table("orders")
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)

        return result_list

    def read_Order_Number_X(self, order_number):
        col_names = ["number", "workpiece", "quantity", "duedate", "latepen", "earlypen", "clientid"]
        rows = self.read_Values("orders", "number,workpiece,quantity,duedate,latepen,earlypen,clientid",
                                f"number='{order_number}'")
        result_list = []
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
        return result_list

    def read_X_Orders(self, number_of_orders):
        col_names = ["number", "workpiece", "quantity", "duedate", "latepen", "earlypen", "clientid"]
        rows = self.read_Table("orders")
        result_list = []
        a = 0
        for row in rows:
            if a == number_of_orders:
                break
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
            a = a + 1
        return result_list

    def Latest_Due_Date(self):
        Latest = self.get_Max("Orders", "duedate")
        return Latest

    def read_Workpiece(self, number):
        self.read_Value(self, "orders", "piecetype", f"number='{number}'")


class Clients(Database):

    # Clients table subclass

    def add_Client(self, client_name):
        self.insert_Row("clients", f"'{client_name}'")

    def delete_Client(self, client_name):
        self.delete_Row("clients", f"clientid='{client_name}'")

    def check_Client(self, clientid):
        return self.check_Amount("clients", f"clientid='{clientid}'")


class Days(Database):

    # Days table subclass

    def Insert_Day(self, Day, Order1, Order2, Order3, Order4):
        self.insert_Row("Days", f"{Day},'{Order1}','{Order2}','{Order3}','{Order4}'")

    def Delete_Day(self, Day):
        self.delete_Row("Days", f"Day={Day}")

    def Update_Order(self, Day, Order_Number, New_Order):
        self.update_Value("Days", f"Day={Day}", f"Order{Order_Number}='{New_Order}'")

    def Update_Current_Day(self):
        Ord1 = self.read_Value("Days", "Order1", "Day=0")
        Ord2 = self.read_Value("Days", "Order2", "Day=0")
        Ord3 = self.read_Value("Days", "Order3", "Day=0")
        Ord4 = self.read_Value("Days", "Order4", "Day=0")
        self.update_Value("Current_Day", "ID=0", f"Order1='{Ord1}',Order2='{Ord2}',Order3='{Ord3}',Order4='{Ord4}'")

    def create_Schedule(self, number_of_days):
        i = 0
        while i < number_of_days:
            self.Insert_Day(i, "", "", "", "")
            i = i + 1

    def delete_Schedule(self):
        days = self.get_Max("Days", "Day")
        while days > 0:
            self.Delete_Day(days)
            days = days - 1

    def next_Day(self):
        days = self.get_Max("Days", "Day")
        i = 0
        while i < days - 1:
            Ord1 = self.read_Value("Days", "Order1", f"Day={i + 1}")
            Ord2 = self.read_Value("Days", "Order2", f"Day={i + 1}")
            Ord3 = self.read_Value("Days", "Order3", f"Day={i + 1}")
            Ord4 = self.read_Value("Days", "Order4", f"Day={i + 1}")
            self.Update_Order(i, "1", Ord1)
            self.Update_Order(i, "2", Ord2)
            self.Update_Order(i, "3", Ord3)
            self.Update_Order(i, "4", Ord4)
            i = i + 1
        self.Delete_Day(days)


class PieceTime(Database):

    # Piecetime table subclass

    def add_Piece(self, piecetype, time):
        self.insert_Row("piecetime", f"{piecetype},'{time}'")

    def delete_Piece(self, piecetype):
        self.delete_Row("piecetime", f"piecetype='{piecetype}'")

    def Update_Time(self, piecetype, time):
        self.update_Value("piecetime", f"piecetype='{piecetype}'", f"time={time}")

    def read_PieceTime(self, piecetype):
        self.read_Value("piecetype", "time", f"piecetype='{piecetype}'")


class Stock(Database):

    # Stock table subclass

    def add_Piece_Type(self, type, quantity):
        self.insert_Row("stock", f"'{type}',{quantity}")

    def delete_Piece_Type(self, type):
        self.delete_Row("stock", f"piece='{type}'")

    def update_Stock(self, type, new_quantity):
        self.update_Value("stock", f"piece='{type}'", f"quantity={new_quantity}")

    def update_Stock_P1(self, P1):
        self.update_Stock("P1", P1)

    def update_Stock_P2(self, P2):
        self.update_Stock("P2", P2)

    def read_Stock_P1(self):
        return self.read_Value("stock", "quantity", "piece='P1'")

    def read_Stock_P2(self):
        return self.read_Value("stock", "quantity", "piece='P2'")


class Statistics(Database):

    # Statistics Table subclass

    def add_statistics_Row(self, number, dc, pc, ad, dd, tc, rc):
        self.insert_Row("statistics", f"'{number}','{dc}','{pc}','{ad}','{dd}','{tc}','{rc}'")

    def update_dc(self, number, dc):
        self.update_Value("statistics", f"number='{number}'", f"dc='{dc}'")

    def update_pc(self, number, pc):
        self.update_Value("statistics", f"number=' {number}'", f"pc='{pc}'")

    def update_ad(self, number, ad):
        self.update_Value("statistics", f"number=' {number}'", f"ad={ad}")

    def update_dd(self, number, dd):
        self.update_Value("statistics", f"number=' {number}'", f"dd='{dd}'")

    def update_rc(self, number, rc):
        self.update_Value("statistics", f"number='{number}'", f"rc='{rc}'")

    def update_tc(self, number, tc):
        self.update_Value("statistics", f"number=' {number}'", f"tc='{tc}'")

    def read_dc(self, number):
        return self.read_Value("statistics", "dc", f"number=' {number}'")

    def read_pc(self, number):
        return self.read_Value("statistics", "pc", f"number=' {number}'")

    def read_rc(self, number):
        return self.read_Value("statistics", "rc", f"number=' {number}'")

    def read_ad(self, number):
        return self.read_Value("statistics", "ad", f"number=' {number}'")

    def read_dd(self, number):
        return self.read_Value("statistics", "dd", f"number=' {number}'")

    def read_tc(self, number):
        return self.read_Value("statistics", "tc", f"number=' {number}'")

    def delete_statistics_row(self, number):
        self.delete_Row("statistics", f"number='{number}'")

    # def calculate_Formulas(self,number,dispatch_date,arrival_date,raw_material_cost,production_time):
    #     pc=production_time
    #     dc=raw_material_cost*(dispatch_date-arrival_date)*0.01
    #     tc=dc+pc+raw_material_cost
    #     self.update_rc(number,raw_material_cost)
    #     self.update_tc(number,tc)
    #     self.update_dc(number,dc)
    #     self.update_pc(number,pc)
    #     self.update_dd(number,dispatch_date)
    #     self.update_ad(number,arrival_date)
    def calculate_formulas(self, number):
        # we only send dispatch_date, arrival_date and raw_material_cost
        piecetype = self.read_Value("orders", "workpiece",
                                    f"number='{number}'")  # SELECT {value} FROM {table_name} WHERE {condition};
        dispatch_date = self.read_dd(number)
        arrival_date = self.read_ad(number)
        raw_material_cost = self.read_rc(number)
        pc = self.read_Value("piecetime", "time", f"pieces='{piecetype}'")  # comes from the piecetime
        dc = raw_material_cost * (dispatch_date - arrival_date) * 0.01
        tc = dc + pc + raw_material_cost
        # self.update_rc(number,raw_material_cost)
        self.update_tc(number, tc)
        self.update_dc(number, dc)
        self.update_pc(number, pc)
        # self.update_dd(number,dispatch_date)
        # self.update_ad(number,arrival_date)

    def get_order_total_cost(self, number):
        self.calculate_formulas(number)
        return self.read_tc(number)

    def read_All_Order_Numbers(self):
        return self.get_column_values("statistics", "number")

    def update_All_RC(self, rc):
        numbers = self.read_All_Order_Numbers()
        for i in range(len(numbers)):
            self.update_rc(numbers[i], rc)


class PiecestoPurchase(Database):
    def add_Piece_To_Purchase(self, piece, quantity, date):
        self.insert_Row("piecestopurchase", f"'{piece}','{quantity}','{date}'")

    def delete_Piece_To_Purchase(self, piece):
        self.delete_Row("piecestopurchase", f"piece='{piece}'")

    def read_PieceQuantity(self, piece):
        self.read_Value("piecestopurchase", "quantity", f"piece='{piece}'")

    def read_Pieces_To_Purchase_Date(self, piece):
        self.read_Value("piecestopurchase", "date", f"piece='{piece}'")

    def Update_Pieces_To_Purchase_Date(self, piece, date):
        self.update_Value("piecestopurchase", f"piece='{piece}'", f"date='{date}'")

    def Update_Pieces_To_Purchase_Quantity(self, piece, quantity):
        self.update_Value("piecestopurchase", f"piece='{piece}'", f"quantity='{quantity}'")


'''
Example code

db=Database()
ord=Orders()
result=ord.read_X_Orders(2)
print(result[1])
ord.close
db.close() 

Note: Always close connection after finishing using it
'''
