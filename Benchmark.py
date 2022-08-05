import os,time,shutil
import pexpect
from pexpect import popen_spawn


graalpath = r"C:/Games/PolyMC-Windows-Portable-1.4.0/graalvm-ee-java17-22.2.0/bin/java.exe"

jdkpath = r"C:/Users/Alpha/Downloads/OpenJDK17U-jre_x64_windows_hotspot_17.0.4_8/jdk-17.0.4+8-jre/bin/java.exe"

commonsuffix = r"@libraries/net/minecraftforge/forge/1.18.2-40.1.60/win_args.txt %* --nogui"

aikar = r'''-Xms6G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1'''

jflags=r'''-server -Xms6G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -Dsun.rmi.dgc.server.gcInterval=2147483646 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -XX:+UseStringDeduplication -XX:+UseFastUnorderedTimeStamps -XX:+UseAES -XX:+UseAESIntrinsics -XX:AllocatePrefetchStyle=1 -XX:+UseLoopPredicate -XX:+RangeCheckElimination -XX:+EliminateLocks -XX:+DoEscapeAnalysis -XX:+UseCodeCacheFlushing -XX:+UseFastJNIAccessors -XX:+OptimizeStringConcat -XX:+UseCompressedOops -XX:+UseThreadPriorities -XX:+OmitStackTraceInFastThrow -XX:+TrustFinalNonStaticFields -XX:ThreadPriorityPolicy=1 -XX:+UseInlineCaches -XX:+RewriteBytecodes -XX:+RewriteFrequentPairs -XX:+UseNUMA -XX:-DontCompileHugeMethods -XX:+UseFPUForSpilling -XX:+UseVectorCmov -Djdk.nio.maxCachedBufferSize=262144 -Dgraal.CompilerConfiguration=community -Dgraal.SpeculativeGuardMovement=true --add-modules jdk.incubator.vector -XX:+UseFMA -XX:+UseNewLongLShift -XX:+UseXMMForArrayCopy -XX:+UseXmmI2D -XX:+UseXmmI2F -XX:+UseXmmLoadAndClearUpper -XX:+UseXmmRegToRegMoveAll -XX:+UseNewLongLShift'''

gflags = r'''-server -Xms6G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -Dsun.rmi.dgc.server.gcInterval=2147483646 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -XX:+EnableJVMCIProduct -XX:+EnableJVMCI -XX:+UseJVMCICompiler -XX:+EagerJVMCI -XX:+UseFastUnorderedTimeStamps -XX:AllocatePrefetchStyle=1 -XX:+TrustFinalNonStaticFields -XX:ThreadPriorityPolicy=1 -XX:+UseNUMA -XX:-DontCompileHugeMethods -XX:+UseVectorCmov -Djdk.nio.maxCachedBufferSize=262144 -Dgraal.TuneInlinerExploration=1 -Dgraal.CompilerConfiguration=enterprise -Dgraal.UsePriorityInlining=false -Dgraal.Vectorization=true -Dgraal.OptDuplication=true -Dgraal.DetectInvertedLoopsAsCounted=true -Dgraal.LoopInversion=true -Dgraal.VectorizeHashes=true -Dgraal.EnterprisePartialUnroll=true -Dgraal.VectorizeSIMD=false -Dgraal.StripMineNonCountedLoops=true -Dgraal.SpeculativeGuardMovement=true -Dgraal.InfeasiblePathCorrelation=true -Dgraal.LoopRotation=true -Dgraal.EarlyGVN=true -Dgraal.StripMineCountedLoops=true -Dlibgraal.ExplicitGCInvokesConcurrent=true -Dlibgraal.AlwaysPreTouch=true -Dlibgraal.ParallelRefProcEnabled=true --add-modules jdk.incubator.vector -XX:+UseFMA -XX:JVMCIThreads=8 -XX:+AlignVector'''

benchlist = [
  jdkpath + " " + aikar + " " + commonsuffix,
  jdkpath + " " + jflags + " " + commonsuffix,
  graalpath + " " + gflags + " " + commonsuffix
]

pathlist = [
  r"C:/Games/atm7"
] * 3

chunkgen_command = r"/forge generate 0 0 0 2000"
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
  child.expect_exact(r'''! For help, type "help"''') #Wait until chunk generation is finished
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
  