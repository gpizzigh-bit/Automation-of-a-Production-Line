import psycopg2

class Database():
    def __init__(self):
        
       # Initialize the database class with the connection parameters.
        
        self.dbname ="d42s9l8fg14nqm"
        self.user = "trroxnzyvifgnt"
        self.password = ""
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

    def read_Value(self,table_name,value,condition):
        query=f"SELECT {value} FROM {table_name} WHERE {condition};"
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.fetchone()[0]  

class Stock(Database):

    #Stock table subclass

    def add_Piece_Type(self,type,quantity):
        self.insert_Row("stock",f"'{type}',{quantity}")
    def delete_Piece_Type(self,type):
        self.delete_Row("stock",f"piece={type}")
    def update_Stock(self,type,new_quantity):
        self.update_Value("stock",f"piece={type}",f"quantity={new_quantity}")
    def update_Stock_P1_P2(self,P1,P2):
        self.update_Stock("P1",P1)
        self.update_Stock("P2",P2)