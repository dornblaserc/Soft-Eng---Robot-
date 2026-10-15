import mysql.connector
from pymycobot.mycobot import MyCobot
import time

def doPickUpPutDown(mc):
   delay = 1
   neutral = [0, 0, 0, 0, 0, 0]
   mc.send_angles(neutral, 50)
   time.sleep(delay)
   mc.set_gripper_value(100,100)
   time.sleep(delay)
   mc.send_angles([-78,0,0,0,0,(-30)],50)
   time.sleep(delay)
   mc.send_angles([(-78),(-25),(-125),70,0,(-30)],50)
   time.sleep(delay*3)
   mc.set_gripper_value(80,100)
   time.sleep(delay)
   mc.send_angles([0,0,0,0,(-90),(-45)],50)
   time.sleep(delay*3)
   mc.send_angles([0,0,0,0,(-90),(-90)],50)
   time.sleep(delay)
   mc.send_angles([0,0,0,0,(-90),(0)],50)
   time.sleep(delay)
   mc.send_angles([0,0,0,0,(-90),(-45)],50)
   time.sleep(delay)
   mc.send_angles([(-78),(-25),(-125),70,0,(-30)],50)
   time.sleep(delay*3)
   mc.set_gripper_value(100,100)
   time.sleep(delay)
   mc.send_angles([-78,0,0,0,0,(-30)],50)
   time.sleep(delay)
   mc.send_angles(neutral, 50)
   time.sleep(delay)

def doThrowBall(mc):
   delay = 1
   neutral = [0, 0, 0, 0, 0, 0]
   pose1 = [90, 90, 0, 0, -90, 90]
   pose2 = [90, 0, 0, 0, -90, 90]
   pose3 = [90, -90, 0, 0, -90, 90]
   mc.send_angles(neutral, 50)
   time.sleep(delay)
   mc.send_angles(pose1, 50)
   time.sleep(delay)
   mc.send_angles(pose2, 50)
   time.sleep(delay)
   mc.send_angles(pose3, 50)
   time.sleep(delay)
   mc.send_angles(neutral, 50)
   time.sleep(delay)

def doWave(mc):
   cycles = 3
   delay = 1
   neutral = [0, 0, 0, 0, 0, 0]
   adjustwrist = [0, 0, 0, 0, -90, 0]
   mc.send_angles(neutral, 50)
   time.sleep(1)
   mc.send_angles(adjustwrist, 50)
   time.sleep(1)
   for c in range(cycles):
      mc.send_angles([0, 15, 15, 15, -90, 0], 25)
      time.sleep(delay)
      mc.send_angles([0, -15, -15, -15, -90, 0], 25)
      time.sleep(delay)
   mc.send_angles(neutral, 50)
   time.sleep(delay)

def doWiggle(mc):
   cycles = 3
   delay = 1
   neutral = [0, 0, 0, 0, 0, 0]
   mc.send_angles(neutral, 50)
   time.sleep(1)
   for c in range(cycles):
      mc.send_angles([0, 30, -45, 30, 0, 0], 50)
      time.sleep(delay)
      mc.send_angles([0, -30, 45, -30, 0, 0], 50)
      time.sleep(delay)
   mc.send_angles(neutral, 50)
   time.sleep(delay)

def doPush(mc):
   delay = 1
   neutral = [0, 0, 0, 0, 0, 0]
   mc.send_angles(neutral, 50)
   time.sleep(delay)
   mc.send_angles([(-90),0,0,0,0,0],90)
   time.sleep(delay)
   mc.send_angles([(-90),0,(-120),0,0,(-50)],90)
   time.sleep(delay)
   mc.set_gripper_value(0,100)
   time.sleep(delay)
   mc.send_angles([(-85),(-27),(-95),30,0,(-50)],90)
   time.sleep(delay)
   mc.set_gripper_value(100,100)
   time.sleep(delay)
   mc.send_angles(neutral, 50)
   time.sleep(delay)

mc = MyCobot('/dev/ttyAMA0',1000000)
# User names and passwords for db connection
dbuser="u413142534_robotworks"
dbpwd="two1x/Y9"
dbaddress="srv557.hstgr.io"
dbname="u413142534_robotworksdb"
#make connection
cnx = mysql.connector.connect(user=dbuser, password=dbpwd,
                              host=dbaddress,
                              database=dbname)

print("Select all from User table")

#need to have this in a try block in case the connect didn't work
try:
    #start a database cursor
   cursor = cnx.cursor()
   cursor.execute("""
         DELETE FROM Instruction WHERE InsID > 0;
      """)   
   while True:
      #send in SQL
      cursor.execute("""
         SELECT * from Instruction;
      """)
      table = cursor.fetchall()
      if table:
         print(f"Data in Instruction Table:")
         for row in table:
            print(row[0], row[1], row[2], row[3], row[4],row[5])
            if (row[4] == 'Not started'):
               if row[3] == 'Pick up put down':
                  doPickUpPutDown(mc)
               elif row[3] == 'Throw ball':
                  doThrowBall(mc)
               elif row[3] == 'Wave':
                  doWave(mc)
               elif row[3] == 'Wiggle':
                  doWiggle(mc)
               elif row[3] == 'Push':
                  doPush(mc)
               update_sql = """
                  UPDATE Instruction
                  SET Status = %s
                  WHERE InsID = %s
               """
               cursor.execute(update_sql, ("Complete", row[0]))
               cnx.commit()
               time.sleep(1)
      else:
         print(f"Empty table.")
   
#always execute the finally block even if the try breaks
       #(There are a limited number of db connections per hour on the system --I think 500 for my Hostinger site)
       # Always close the connection to free up connections on the DB.
finally:
    cnx.close()
