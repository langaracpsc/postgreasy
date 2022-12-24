#!/usr/bin/env python3


import psycopg2
import json
import sys
import uuid

class Tools:
    def TrimString(string: str, length: int):
        trimmedString = str()

        if (not(length in range(len(string)))):
            return string
        for x in range(length):
            trimmedString += string[x]
        return trimmedString

    def IsSubSet(array: list, sArray: list):
        for val in array:
            if (not(val in sArray)):
                return bool(0)
        return bool(1)

class FileIO:
    def Read(path: str):
        return open(path, 'r').read()

    def Write(data: str, path: str):
        open(path, 'w').write(data)

class DatabaseConfig:
    Name = str
    User = str

    def __init__(self, name: str, user: str):
        self.Name = name
        self.User = user

    def ToString(self):
        return str(f"dbname={self.Name} user={self.User}")

class DBTools:
    def GetSQLFormatted(val):
        if (type(val) == str or type(val) == chr):
            return str(f"\'{val}\'")
        return val

    def GetSQLValueString(tup: tuple):
        tupleString = str('(')

        for x in range(len(tup) - 1):
            tupleString += f"{DBTools.GetSQLFormatted(tup[x])}, "

        tupleString += f"{DBTools.GetSQLFormatted(tup[len(tup) - 1])})"

        return tupleString

    def GetSQLSetString(recordDict: dict):
        setString = str()
        fields = list(recordDict.keys())

        end = len(fields) - 1

        for x in range(end):
            setString += f"{fields[x]}={DBTools.GetSQLFormatted(recordDict[fields[x]])}, "

        setString += f"{fields[end]}={DBTools.GetSQLFormatted(recordDict[fields[end]])}"

        return setString



class Database:
    ConfigPath = str
    Config = DatabaseConfig

    Cursor = None

    Connection = None

    IsConnected = bool(0)

    def LoadConfig(self):
        try:
            if (self.ConfigPath == None or self.ConfigPath == str()):
                raise BaseException("No config file provided.")

            configDict = json.loads(FileIO.Read(self.ConfigPath))
            self.Config = DatabaseConfig(configDict["dbname"], configDict["user"])

        except json.JSONDecodeError:
            raise BaseException("Invalid config provided, please check the format.")


    def __init__(self, configPath: str):
        self.ConfigPath = configPath
        self.LoadConfig()

    def Connect(self):
        self.Connection = psycopg2.connect(self.Config.ToString())
        self.Cursor = self.Connection.cursor()

    def Disconnect(self):
        self.Cursor.close()
        self.Connection.close()


    def ExecuteCommand(self, command: str):
        result = self.Cursor.execute(command)

        self.Connection.commit()

        return result

    def FetchQueryData(self, query: str):
        self.Cursor.execute(query)

        result = self.Cursor.fetchone()

        tupleStack = list[tuple]()

        while (result != None):
            tupleStack.append(result)
            result = self.Cursor.fetchone()

        return tupleStack

    def GetFieldNames(self, table: str) -> list:
        fieldStack = list()
        result = self.FetchQueryData(f"""
            SELECT column_name FROM information_schema.columns WHERE table_name=\'{table}\';
        """)

        for tup in result:
            fieldStack.append(tup[0])
        return fieldStack

    def InsertRecord(self, record: tuple, table: str):
        self.ExecuteCommand(f"INSERT INTO {table} VALUES{DBTools.GetSQLValueString(record)}")

        return bool(1)

    def UpdateRecord(self, record: dict, condition: dict, table: str)->bool:
        fieldNames = self.GetFieldNames(table)

        if (not(Tools.IsSubSet(list(record.keys()), fieldNames)) or not(Tools.IsSubSet(list(condition.keys()), fieldNames))):
            raise BaseException("Field names of the provided record dont match the fields of the table.")

        self.ExecuteCommand(f"UPDATE {table} SET {DBTools.GetSQLSetString(record)} WHERE {DBTools.GetSQLSetString(condition)};")
        return bool(1)

    def DeleteRecord(self, condition: dict, table: str):
        if (not(Tools.IsSubSet(list(condition.keys()), self.GetFieldNames(table)))):
            raise BaseException("Field names of the provided record dont match the fields of the table.")
        print(f"DELETE FROM {table} WHERE {DBTools.GetSQLSetString(condition)};")
        self.ExecuteCommand(f"DELETE FROM {table} WHERE {DBTools.GetSQLSetString(condition)};")
        return bool(0)

def Main(args: list):
    db = Database("config.json")
    db.Connect()
    #db.InsertRecord(tuple((Tools.TrimString(str(uuid.uuid4()), 36), args[1])), args[2])
    print(db.FetchQueryData("SELECT * FROM test;"))
    print(db.GetFieldNames("test"))
    db.DeleteRecord(dict({args[1]: args[2]}), "test")

    db.Disconnect()

Main(sys.argv)
