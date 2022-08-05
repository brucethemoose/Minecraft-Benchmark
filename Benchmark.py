import os,pexpect,time,itertools

benchlist = [
  "command",
  "command2"
]

pathlist = [
  "path1",
  "path2"
]

chunkgen_command = r"/forge pregen 5000"
chunkgen_expect =  r"Finished generating"

def benchmark(benchcmd, benchpath):
  os.chdir(benchpath)
  os.rename("world","_worldbackup") #Backup minecraft world
  start = time.time()
  with pexpect.spawn(benchcmd) as child:   #Start Minecraft server
    child.expect (r'[minecraft/DedicatedServer]: Done (') #Wait until chunk generation is finished
    startuptime = time.time() - start
    time.sleep(25)    #Let the server "settle"
    start = time.time()
    child.sendline (chunkgen_command)   #Generate chunks
    child.expect (chunkgen_expect)
    chunkgentime = time.time() - start
    child.sendline ('stop')     #shutdown the minecraft server
    time.sleep(8) # just in case
  os.remove("world")
  os.rename("_worldbackup", "world")  #restore backup
  return chunkgentime, startuptime

for (bench,path) in zip(benchlist,pathlist):
  ctime,stime = benchmark(bench,path)
  print("Path: " + path)
  print("Command: " + bench)
  print(" ")
  print ("Startup Time: " + stime)
  print("Chunk Generation Time:" + ctime)
  print (" ")
  