import os,sys,subprocess,pexpect

benchlist = [
  "command",
  "command2"
]

pathlist = [
  "path1",
  "path2"
]

def benchmark(benchcmd, benchpath):
  os.chdir(benchpath)
  os.rename("world","_worldbackup")
  child = pexpect.spawn(benchcmd)
  child.expect ('Finished Generating World')
  child.sendline ('anonymous')
child.expect ('Password:')
child.sendline ('noah@example.com')
child.expect ('ftp> ')
child.sendline ('ls /pub/OpenBSD/')
child.expect ('ftp> ')
print child.before   # Print the result of the ls command.
child.interact()     # Give control of the child to the user.
