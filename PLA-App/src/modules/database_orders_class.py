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
        
        
    def delete_Table(self,table_name):
       
        #Delete table with given parameters

        query=f"DROP TABLE {table_name};"
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


class Concluded(Database):

    # # Concluded orders table subclass
    # Add_Order adds an order number to the concluded orders table
    # Delete_Order deletes an order by its number
    # Read All_Orders returns an array of strings, each string corresponds to an order and contains all its values: number,piecetype,date,etc
    def add_Order(self,number):  
        self.insert_Row("concluded",f"{number}")
    def delete_Order(self,number):
        self.delete_Row("concluded",f"number={number}")
    def read_All_Orders(self):
        col_names=["number"]
        result_list=[]
        rows=self.read_Table("concluded")
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)

        return result_list   

class Pending(Database):

    # Pending orders table subclass
    # Add_Order adds an order number to the pending orders table
    # Delete_Order deletes an order by its number
    # Read All_Orders returns an array of strings, each string corresponds to an order and contains all its values: number,piecetype,date,etc
    def add_Order(self,number):
        self.insert_Row("pending",f"{number}")
    def delete_Order(self,number):
        self.delete_Row("pending",f"number={number}")
    def read_All_Orders(self):
        col_names=["number"]
        result_list=[]
        rows=self.read_Table("pending")
        for row in rows:
            row_strings = [f"{col_names[i]}: {str(row[i])}" for i in range(len(col_names))]
            row_string = '; '.join(row_strings)
            result_list.append(row_string)

        return result_list   


class Orders(Database):

    # Orders table subclass
    # Note: each order number is unique
    # add_Order adds an order to the orders table
    # Note: number,quantity and client id are int type, the other variables are character varying(255)
    # delete_Order deletes and ordery by its number
    # read_All_Orders returns an array of strings, each string contains an order
    # read_Order_Number_X returns an array with the order with the number X.
    # read_X_Orders returns an array with X number of orders 
    

    def add_Order(self,number,workpiece,quantity,duedate,latepen,earlypen,clientid):
        self.insert_Row("orders",f"{number},'{workpiece}','{quantity}','{duedate}','{latepen}','{earlypen}',{clientid}")
    def delete_Order(self,number):
        self.delete_Row("orders",f"number={number}")
    def update_Order(self,number,new_quantity):
        self.update_Value("orders",f"number={number}",f"{new_quantity}")
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
