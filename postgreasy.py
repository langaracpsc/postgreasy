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

    def GetSQLValueString(tup: tuple):
        tupleString = str('(')

        for x in range(len(tup) - 1):
            tupleString += f"{DBTools.GetSQLFormatted(tup[x])}, "

        tupleString += f"{DBTools.GetSQLFormatted(tup[len(tup) - 1])})"

        return tupleString


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

    def InsertRecord(self, record: tuple, table: str):
        print(f"INSERT INTO {table} VALUES({DBTools.GetSQLValueString(record)})")
        self.ExecuteCommand(f"INSERT INTO {table} VALUES{DBTools.GetSQLValueString(record)}")
        return



def Main(args: list):
    db = Database("config.json")
    db.Connect()
    db.InsertRecord(tuple((Tools.TrimString(str(uuid.uuid4()), 36), args[1])), args[2])
    db.Disconnect()

Main(sys.argv)
