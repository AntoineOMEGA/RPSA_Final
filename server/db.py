import sqlite3
import os.path

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class LocationsDB:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "locationsDB.db")
        with sqlite3.connect(db_path) as self.connection:
            self.connection.row_factory = dict_factory
            self.cursor = self.connection.cursor()

    #USERS
    def insertUser(self, firstname, lastname, email, password):
        data = [firstname, lastname, email, password]
        self.cursor.execute("INSERT INTO users (firstname, lastname, email, password) VALUES (?,?,?,?)", data)
        self.connection.commit()
    
    def getUser(self, email):
        data = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = ?", data)
        result = self.cursor.fetchall()
        if result == []:
            return False
        else:
            return result

    #LOCATIONS
    def insertLocation(self, title, latitude, longitude, description, category):
        data = [title, latitude, longitude, description, category]
        #data binding fix
        self.cursor.execute("INSERT INTO locations (title, latitude, longitude, description, category) VALUES (?,?,?,?,?)", data)
        self.connection.commit()
    
    def getLocations(self):
        self.cursor.execute("SELECT * FROM locations")
        result = self.cursor.fetchall()
        return result
        #return list of dictionaries
    
    def getLocation(self, location_id):
        data = [location_id]
        self.cursor.execute("SELECT * FROM locations WHERE id = ?", data)
        result = self.cursor.fetchone()
        return result
        #return individual record dictionary
    
    def deleteLocation(self, location_id):
        data = [location_id]
        self.cursor.execute("DELETE FROM locations WHERE id = ?", data)
        self.connection.commit()
        return "Deleted"
    
    def updateLocation(self, location_id, title, description, category):
        data = [title, description, category, location_id]
        self.cursor.execute("UPDATE locations SET title=?, description=?, category=? WHERE id = ?", data)
        self.connection.commit()
        return "Updated"


'''
SQL Injection
use data binding as fix for sql injection
'''