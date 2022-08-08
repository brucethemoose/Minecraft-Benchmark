import os,time,shutil,glob,logging,datetime,sys,traceback
import signal
import platform
import pexpect
import psutil
from pexpect import popen_spawn




#----Minecraft Paths-----

atm7 = r"C:/Games/atm7"

vev = r"C:/Games/vevserver"

#----Java Paths-----

graalpath = r"C:/Games/PolyMC-Windows-Portable-1.4.0/graalvm-ee-java17-22.2.0/bin/java.exe"

jdkpath = r"C:/Users/Alpha/Downloads/OpenJDK17U-jre_x64_windows_hotspot_17.0.4_8/jdk-17.0.4+8-jre/bin/java.exe"

j9path = r"C:/Users/Alpha/Downloads/ibmopenj9/bin/java.exe"

gbackpath = r"C:/Users/Alpha/Downloads/graalvm-ee-java17-windows-amd64-22.1.0/graalvm-ee-java17-22.1.0/bin/java.exe"

#----Java Flags-----
#(Should start with a space)

aikar = r''' -server -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1'''

graal = r''' -server -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -Dsun.rmi.dgc.server.gcInterval=2147483646 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -XX:+EnableJVMCIProduct -XX:+EnableJVMCI -XX:+UseJVMCICompiler -XX:+EagerJVMCI -XX:+UseFastUnorderedTimeStamps -XX:AllocatePrefetchStyle=3 -XX:+TrustFinalNonStaticFields -XX:ThreadPriorityPolicy=1 -XX:+UseNUMA -XX:-DontCompileHugeMethods -XX:+UseVectorCmov -Djdk.nio.maxCachedBufferSize=262144 -Dgraal.TuneInlinerExploration=1 -Dgraal.CompilerConfiguration=enterprise -Dgraal.UsePriorityInlining=true -Dgraal.Vectorization=true -Dgraal.OptDuplication=true -Dgraal.DetectInvertedLoopsAsCounted=true -Dgraal.LoopInversion=true -Dgraal.VectorizeHashes=true -Dgraal.EnterprisePartialUnroll=true -Dgraal.VectorizeSIMD=true -Dgraal.StripMineNonCountedLoops=true -Dgraal.SpeculativeGuardMovement=true -Dgraal.InfeasiblePathCorrelation=true -Dgraal.LoopRotation=true -Dlibgraal.ExplicitGCInvokesConcurrent=true -Dlibgraal.AlwaysPreTouch=true -Dlibgraal.ParallelRefProcEnabled=true'''

lpages = r''' -XX:+UseLargePages -XX:LargePageSizeInBytes=2m'''

memory = r''' -Xms4G -Xmx4G'''

#Assemble your testing commands with the above strings
#Forge/Fabric packs only need "java + arguments", as their jars are automatically found

javalist = [
  gbackpath + memory + graal + lpages,
  gbackpath + memory + graal + lpages
]

#List of Minecraft paths. The length of this list should be the same as the java list
#Forge/Fabric
pathlist = [
  atm7,
  vev
]


#----Other Options-----

nogui = False
carpet = 0 #number of simulated carpet players
#Fabric
fabric_chunkgen_command = r"chunky start"                #Chunk generation command to use
fabric_chunkgen_expect =  r"[Chunky] Task finished for"  #String to look for when chunk generation is finished
#Forge
forge_chunkgen_command = r"forge generate 0 0 0 3000"
forge_chunkgen_expect =  r"Finished generating"

startuptimeout= 600
chunkgentimeout = 1000
iterations = 1
debug = False #Print stages of when the server starts/runs




def benchmark(java, mcpath, carpet = 0):

  def restore():
    if os.path.isdir("world"):
      shutil.rmtree("world")
    if os.path.isdir("_worldbackup"):
        os.rename("_worldbackup", "world")  #restore backup


  #Init
  spark = False
  chunkgentime = 0
  startuptime = 0
  chunkgen_command = ""
  chunkgen_expect = ""
  os.chdir(mcpath)
  plat = "Linux"
  if "Windows" in platform.system():
    plat = "Windows"
  ngui = ""
  if nogui:
    ngui = " nogui"

  #Start building the Minecraft command
  if plat == "Linux":
    command = "nice -n -18 " + java
  else:
    command = java

  #Try to find fabric
  d = glob.glob("*.jar")
  for f in d:
    if "fabric-" in os.path.basename(f):
      if debug: print("Found Fabric: " + f)
      chunkgen_command = fabric_chunkgen_command
      chunkgen_expect = fabric_chunkgen_expect
      command = command + " -jar " + os.path.basename(f)
      #Delete chunky config if found
      if os.path.isfile(r"config/chunky.json"):
        if debug: print("Removing chunky config")
        os.remove(r"config/chunky.json")

  
  #Try to find forge
  d = glob.glob(r"libraries/net/minecraftforge/forge/*/win_args.txt")
  if len(d) == 1:
    if debug: print("Found Forge" + d[0])
    chunkgen_command = forge_chunkgen_command
    chunkgen_expect = forge_chunkgen_expect
    if plat == "Linux":
      command = command + " @" + os.path.normpath(os.path.join(os.path.dirnamme(d[0]), r"unix_args.txt")) + ngui + r' "$@"'
    else:
       command = command + " @" + os.path.normpath(d[0]) + r" %*"
       if nogui:
        command = command + " --nogui"
    

  #Try to find Spark and/or Carpet mods
  if os.path.isdir("mods"):
    mods = glob.glob("mods/*.jar")
    spark = any(s.startswith('spark') for s in mods) #Check for Spark mod
    if debug: print("Spark: " + str(spark))
    if any(s.startswith('fabric-carpet') for s in mods):
      if debug: print("Carpet Players: " + str(carpet))
    else:
      carpet = 0
      if debug: print("Carpet: False")
  else: 
    if debug: print("No mods folder found")

  #Backup Minecraft world.
  if os.path.isdir("world"):
    if os.path.isdir("_worldbackup"):
      shutil.rmtree("_worldbackup")
    os.rename("world","_worldbackup") #Backup minecraft world

  #Helper function
  def qw(s):
    with open("bench.txt", "a") as f:
      f.write("Startup Time: " + s)
      f.write("\n")
      f.write("Chunkgen Time: " + s)
      f.write("\n")

  #Start Minecraft, wrapping pexpect in a big try so we can restore world backups
  try:
    start = time.time()
    with open("bench.txt", "a") as f:
      f.write("Path: " + mcpath)
      f.write("\n")
      f.write("Command: " + command)
      f.write("\n")
    child = pexpect.popen_spawn.PopenSpawn(command, timeout=1200, maxread=2000000,)   #Start Minecraft server
    if debug: print("Starting server: " + command)
    time.sleep(0.01)
    if plat == "Windows":
      try:
        for proc in psutil.process_iter(['pid', 'name']):
          if "java" in str(proc.name):
            if debug: print("Setting Priority")
            proc.nice(psutil.HIGH_PRIORITY_CLASS)
      except:
        print("Failed to set process priority, please run this benchmark as an admin!")
    index = child.expect_exact(pattern_list=[r'''! For help, type "help"''', 'Minecraft Crash Report', pexpect.EOF, pexpect.TIMEOUT], timeout=startuptimeout)
    if index == 0:
      if debug: print("Server started")
    elif index == 1:
      child.sendline('stop')
      child.kill(signal.SIGTERM)
      restore()
      qw("CRASH")
      return "CRASH", "CRASH"
    elif index == 2:
      restore()
      qw("STOPPED")
      return "STOPPED", "STOPPED"
    elif index == 3:
      child.sendline('stop')
      child.kill(signal.SIGTERM)
      restore()
      qw("TIMEOUT")
      return "TIMEOUT", "TIMEOUT"
    startuptime = time.time() - start
    with open("bench.txt", "a") as f:
      f.write("Startup Time: " + str(startuptime))
      f.write("\n")
    time.sleep(13)    #Let the server "settle"
    if debug: print("Generating chunks...")
    start = time.time()
    child.sendline(chunkgen_command)   #Generate chunks
    index = child.expect_exact(pattern_list=[chunkgen_expect, 'Minecraft Crash Report', pexpect.EOF, pexpect.TIMEOUT], timeout=chunkgentimeout)
    if index == 0:
      if debug: print("Chunks finished. Stopping server...")
      chunkgentime = time.time() - start
    elif index == 1:
      chunkgentime = "CRASH"
    elif index == 2:
      chunkgentime = "STOPPED"
    elif index == 3:
      chunkgentime = "TIMEOUT"
    child.kill(signal.SIGTERM)
    with open("bench.txt", "a") as f:
      f.write("Chunkgen Time: " + str(chunkgentime))
      f.write("\n")
      f.write("\n")
  except:
    traceback.print_exc()
    restore()
    print("Exiting!")
    sys.exit()
  restore()
  return chunkgentime, startuptime


#Main thread
for p in set(pathlist):
  os.chdir(p)
  with open("bench.txt", "a") as f:
    f.write("\n")
    f.write("---------------------------------------------------------")
    f.write("\n")
    f.write("Benchmark started at " + str(datetime.datetime.now()))
    f.write("\n")
for x in range(1,iterations + 1):
  for (path,java) in zip(pathlist,javalist):
    results = benchmark(java,path)
    print("Bench completed.")
  print("Iteration done.")
print("Done.")  