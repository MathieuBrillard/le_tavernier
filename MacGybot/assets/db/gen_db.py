import sqlite3

def gen_db():
    # connect to the db
    connection = sqlite3.connect("calendar.db")
    # create cursor to send commands
    cursor = connection.cursor()
    print("connected to database.")
    print("executing commands...")
    command = """
    CREATE TABLE "users" (
        "uid" TEXT PRIMARY KEY,
        "name" TEXT);
    """
    # execute the command
    cursor.execute(command)
    command = """
    CREATE TABLE "events" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "name" TEXT,
        "desc" TEXT,
        "date" TEXT,
        "time" TEXT,
        "server_id" TEXT);
    """
    cursor.execute(command)
    command = """
    CREATE TABLE "u_to_e" (
        "uid" TEXT,
        "event_id" INTEGER);
    """
    cursor.execute(command)
    print("tables created.")
    print("closing database...")
    connection.close()

if __name__ == "__main__":
    gen_db()