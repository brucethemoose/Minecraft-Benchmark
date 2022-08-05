import os,time,shutil
import pexpect
from pexpect import popen_spawn

benchlist = [
  r'''"C:/Games/PolyMC-Windows-Portable-1.4.0/graalvm-ee-java17-22.2.0/bin/java.exe" @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.18.2-40.1.68/win_args.txt %* --nogu'''
]

pathlist = [
  r"C:/Games/minecraft-server"
]

chunkgen_command = r"/forge generate 0 0 0 500"
chunkgen_expect =  r"Finished generating"

debug = True

def benchmark(benchcmd, benchpath):
  os.chdir(benchpath)
  if os.path.isdir("world"):
    if os.path.isdir("_worldbackup"):
      shutil.rmtree("_worldbackup")
    os.rename("world","_worldbackup") #Backup minecraft world
  start = time.time()
  child = pexpect.popen_spawn.PopenSpawn(benchcmd, timeout=1200, maxread=2000000,)   #Start Minecraft server
  if debug: print("Starting server...")
  child.expect_exact(r' Done ') #Wait until chunk generation is finished
  if debug: print("Server started")
  startuptime = time.time() - start
  time.sleep(20)    #Let the server "settle"
  if debug: print("Generating chunks...")
  start = time.time()
  child.sendline(chunkgen_command)   #Generate chunks
  child.expect_exact(chunkgen_expect)
  if debug: print("Chunks finished. Stopping server...")
  chunkgentime = time.time() - start
  child.sendline('stop')     #shutdown the minecraft server
  child.wait()
  shutil.rmtree("world")
  if os.path.isdir("_worldbackup"):
    os.rename("_worldbackup", "world")  #restore backup
  return chunkgentime, startuptime

for (bench,path) in zip(benchlist,pathlist):
  ctime,stime = benchmark(bench,path)
  print("Path: " + str(path))
  print("Command: " + str(bench))
  print(" ")
  print ("Startup Time: " + str(stime))
  print("Chunk Generation Time:" + str(ctime))
  print (" ")
  