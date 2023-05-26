import psycopg2

class Database():
    def __init__(self):
        
       # Initialize the database class with the connection parameters.
        
        self.dbname ="d42s9l8fg14nqm"
        self.user = "trroxnzyvifgnt"
        self.password = "85c17ff132d95b23eca8d735622ee140e9e09913e2dffd69586074c279217cba"
        self.host ="ec2-18-202-8-133.eu-west-1.compute.amazonaws.com"
        self.port = "5432"
        self.conn = psycopg2.connect(
        dbname=self.dbname,
        user=self.user,
        password=self.password,
        host=self.host,
        port=self.port)
        self.cur=self.conn.cursor()

        # Basic Modules to be used in subclasses

    def create_Table(self,table_name,columns):
        
         #Create table with given parameters
        
        query=f"CREATE TABLE if not exists {table_name} ({columns});"
        self.cur.execute(query)
        self.conn.commit()
        
    def check_Amount(self,table_name,condition):
        query=f"SELECT COUNT (*)FROM {table_name} WHERE {condition}"
        self.cur.execute(query)
        self.conn.commit()
        result=self.cur.fetchone()
        return result[0]>0
        
    def delete_Table(self,table_name):
       
        #Delete table with given parameters

        query=f"DROP TABLE {table_name} CASCADE;"
        self.cur.execute(query)
        self.conn.commit()

    def close(self):
        
       # Close the connection to the database
        
        self.cur.close()
        self.conn.close()


    def insert_Row(self,table_name,values):

        # Insert a new row into a table

        query=f"INSERT INTO {table_name} VALUES ({values});"
        self.cur.execute(query)
        self.conn.commit()

    def delete_Row(self,table_name,condition):

        # Delete a row from table

        query=f"DELETE FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()

    def update_Value(self,table_name,condition,new_values):
        query=f"UPDATE {table_name} SET {new_values} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
    
    def read_Values(self,table_name,variables,condition):

        # Fecth all values from a given condition

        query=f"SELECT {variables} FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchall()
    
    def read_Table(self,table_name):

        # Fetch all values from a table

        query=f"SELECT * FROM {table_name};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchall()
    
    def get_Max(self,table_name,column):

        # Get the max value from a column

        query=f"SELECT MAX({column}) from {table_name}"
        self.cur.execute(query)
        result=self.cur.fetchone()[0]
        self.conn.commit()
        return (result)

    def read_Value(self,table_name,value,condition):
        query=f"SELECT {value} FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchone()[0]  
class Concluded(Database):

    # # Concluded orders table subclass
    # Add_Order adds an order number to the concluded orders table
    # Delete_Order deletes an order by its number
    # Read All_Orders returns an array of strings, each string corresponds to an order and contains all its values: number,piecetype,date,etc
    def check_Concluded(self,order):
        return self.check_Amount("concluded",f"number='{order}'")
    def add_Concluded(self,number,workpiece,quantity,duedate,latepen,earlypen,clientid):
        cl=Clients()
        if cl.check_Client(clientid) == True:
            self.insert_Row("concluded",f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        else :
            cl.add_Client(clientid)
            self.insert_Row("concluded",f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        cl.close()
    def delete_Concluded(self,number,clientid):
        self.delete_Row("concluded",f"number='{number}' AND clientid='{clientid}'")
    def update_Concluded(self,number,new_quantity):
        self.update_Value("concluded",f"number={number}",f"quantity={new_quantity}")
    def read_All_Concluded(self):
        col_names=["number","workpiece","quantity","duedate","latepen","earlypen","clientid"]
        result_list=[]
        rows=self.read_Table("concluded")
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)

        return result_list   
    def read_Concluded_Number_X(self,order_number):
        col_names=["number","workpiece","quantity","duedate","latepen","earlypen","clientid"]
        rows=self.read_Values("concluded","number,workpiece,quantity,duedate,latepen,earlypen,clientid",f"number={order_number}")
        result_list=[]
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
        return result_list
    
    def read_X_Concluded(self,number_of_orders):
        col_names=["number","workpiece","quantity","duedate","latepen","earlypen","clientid"]
        rows=self.read_Table("concluded")
        result_list=[]
        a=0
        for row in rows:
            if a==number_of_orders:
                break
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
            a=a+1
        return result_list
    def Latest_Due_Date(self):
        Latest=self.get_Max("concluded","duedate")
        return Latest
class Orders(Database):

    # Orders table subclass
    # Note: each order number is unique
    # add_Order adds an order to the orders table
    # Note: number,quantity and client id are int type, the other variables are character varying(255)
    # delete_Order deletes and ordery by its number
    # read_All_Orders returns an array of strings, each string contains an order
    # read_Order_Number_X returns an array with the order with the number X.
    # read_X_Orders returns an array with X number of orders 
    
    def check_Order(self,order):
        return self.check_Amount("orders",f"number='{order}'")
    def add_Order(self,number,workpiece,quantity,duedate,latepen,earlypen,clientid):
        cl=Clients()
        if cl.check_Client(clientid) == True:
            self.insert_Row("orders",f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        else :
            cl.add_Client(clientid)
            self.insert_Row("orders",f"'{number}','{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}','{clientid}'")
        cl.close()
    def delete_Order(self,number,clientid):
        self.delete_Row("orders",f"number='{number}' AND clientid='{clientid}'")
    def update_Order(self,number,new_quantity):
        self.update_Value("orders",f"number={number}",f"quantity={new_quantity}")
    def read_All_Orders(self):
        col_names=["number","workpiece","quantity","duedate","latepen","earlypen","clientid"]
        result_list=[]
        rows=self.read_Table("orders")
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)

        return result_list   
    def read_Order_Number_X(self,order_number):
        col_names=["number","workpiece","quantity","duedate","latepen","earlypen","clientid"]
        rows=self.read_Values("orders","number,workpiece,quantity,duedate,latepen,earlypen,clientid",f"number={order_number}")
        result_list=[]
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
        return result_list
    
    def read_X_Orders(self,number_of_orders):
        col_names=["number","workpiece","quantity","duedate","latepen","earlypen","clientid"]
        rows=self.read_Table("orders")
        result_list=[]
        a=0
        for row in rows:
            if a==number_of_orders:
                break
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)
            a=a+1
        return result_list
    def Latest_Due_Date(self):
        Latest=self.get_Max("Orders","duedate")
        return Latest
class Clients(Database):

    # Clients table subclass

    def add_Client(self,client_name):
        self.insert_Row("clients",f"'{client_name}'")
    def delete_Client(self,client_name):
        self.delete_Row("clients",f"clientid='{client_name}'")
    def check_Client(self,clientid):
        return self.check_Amount("clients",f"clientid='{clientid}'")
class Days(Database):
    def Insert_Day(self,Day,Order1,Order2,Order3,Order4):
        self.insert_Row("Days",f"{Day},'{Order1}','{Order2}','{Order3}','{Order4}'")
    def Delete_Day(self,Day):
        self.delete_Row("Days",f"Day={Day}")
    def Update_Order(self,Day,Order_Number,New_Order):
        self.update_Value("Days",f"Day={Day}",f"Order{Order_Number}='{New_Order}'")
    def Update_Current_Day(self):
        Ord1=self.read_Value("Days","Order1","Day=0")
        Ord2=self.read_Value("Days","Order2","Day=0")
        Ord3=self.read_Value("Days","Order3","Day=0")
        Ord4=self.read_Value("Days","Order4","Day=0")
        self.update_Value("Current_Day","ID=0",f"Order1='{Ord1}',Order2='{Ord2}',Order3='{Ord3}',Order4='{Ord4}'")
    def create_Schedule(self,number_of_days):
        i=0
        while i<number_of_days:
            self.Insert_Day(i,"","","","")
            i=i+1
    def delete_Schedule(self):
        days=self.get_Max("Days","Day")
        while days>0:
            self.Delete_Day(days)
            days=days-1
    def next_Day(self):
        days=self.get_Max("Days","Day")
        i=0
        while i<days-1:
            Ord1=self.read_Value("Days","Order1",f"Day={i+1}")
            Ord2=self.read_Value("Days","Order2",f"Day={i+1}")
            Ord3=self.read_Value("Days","Order3",f"Day={i+1}")
            Ord4=self.read_Value("Days","Order4",f"Day={i+1}")
            self.Update_Order(i,"1",Ord1)
            self.Update_Order(i,"2",Ord2)
            self.Update_Order(i,"3",Ord3)
            self.Update_Order(i,"4",Ord4)
            i=i+1
        self.Delete_Day(days)    
class PieceTime(Database):
    def add_Piece(self,piecetype,time):
         self.insert_Row("piecetime",f"{piecetype},'{time}'")
    def delete_Piece(self,piecetype):
        self.delete_Row("piecetime",f"piecetype='{piecetype}'")
    def Update_Time(self,piecetype,time):
        self.update_Value("piecetime",f"piecetype={piecetype}",f"time={time}")
        

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
