#!/usr/bin/env python


szWorkToDo = "dirsAndSbatchCommands.txt"

import subprocess
import os
from datetime import datetime


nMaximumNumberOfSimultaneousSubmits = 10
nSecondsToSleep = 10

nNextSubmitCommand = 0

aDirectoriesAndSbatchCommands = []
aRunningJobs = []


# open a log file

szLog = "autoSubmitter.log"

if ( os.path.exists( szLog ) ):
    szNewName = f"{szLog}.{datetime.now():%Y%m%d.%H%M%S}"
    szCommand = f"mv {szLog} {szNewName}"
    subprocess.call( szCommand, shell = True )


fLog = open( szLog, "w" )    


def printLog( szOutput ):
    szOutputWithDateTime = f" {datetime.now():%Y%m%d.%H%M%S} {szOutput}"
    print( f"{szOutputWithDateTime}", file = fLog, flush = True )
    


def waitForAJobToFinish():

    bJobFinished = False

    while( not bJobFinished ):
        
        aRunningJobsCopy = aRunningJobs
        for nJob in aRunningJobsCopy:
            szCommand = "squeue -j " + nJob
            szOutput = subprocess.check_output( szCommand, shell = True ).decode("utf-8")

            printLog( f"{szCommand} and got {szOutput}" )
            
            aLines = szOutput.splitlines()

            # looks like:
            #JobID           JobName  Partition    Account  AllocCPUS      State ExitCode 
            #------------ ---------- ---------- ---------- ---------- ---------- -------- 
            #16687086     run_sleep+    agsmall    hsiehph          1    RUNNING      0:0

            assert len( aLines) >= 1, f"{szCommand} returned {szOutput}"

            szImportantLine = aLines[ len( aLines ) - 1]


            aWords = szImportantLine.split()
            assert len( aWords ) >= 7, f"{szCommand} returned {szOutput} with only" + str( len( aWords ) ) + f" on line {szImportantLine}"

            if ( aWords[0] == "JOBID" ):
                printLog( f"{nJob} finished so removing it from list" )
                aRunningJobs.remove( nJob )
                bJobFinished = True


        if ( not bJobFinished ):
            printLog( f"sleeping" )

            szCommand = f"sleep {nSecondsToSleep}"
            subprocess.call( szCommand, shell = True )

# def waitForAJobToFinish():

        

def submitJob( szDirectoryAndSbatchCommand ):

    printLog( f"about to submit {szDirectoryAndSbatchCommand}" )

    szOutput = subprocess.check_output( szDirectoryAndSbatchCommand, shell = True ).decode("utf-8")

    # should look like:
    # sbatch: Setting account: hsiehph
    # Submitted batch job 16687086
    #  0         1     2    3


    printLog( f"submitted {szDirectoryAndSbatchCommand} and got {szOutput}" )
    
    
    aLines = szOutput.splitlines()
    assert len( aLines ) >= 1, f"{szDirectoryAndSbatchCommand} returned {szOutput} which should have had at least 1 line"


    
    szImportantLine = aLines[ len( aLines ) - 1]
    aWords = szImportantLine.split()
    assert len( aWords ) >= 4, f"{szDirectoryAndSbatchCommand} returned {szOutput} with only" + str( len( aWords ) ) + f" but should have had 4 on line {szImportantLine}"
    szJobID = aWords[3]
    aRunningJobs.append( szJobID )

# def submitJob( szDirectoryAndSbatchCommand ):

    

printLog( f"starting autoSubmitter" )

with open( szWorkToDo, "r" ) as fDirsAndSbatchCommands:
    while True:
        szLine = fDirsAndSbatchCommands.readline()
        if ( szLine == "" ):
            break
        if ( szLine.startswith( '#' )):
            continue
        szLine = szLine.rstrip()
        if ( szLine == "" ):
            continue
        aDirectoriesAndSbatchCommands.append( szLine )


while True:

    while( ( len( aRunningJobs ) < nMaximumNumberOfSimultaneousSubmits ) and nNextSubmitCommand <len( aDirectoriesAndSbatchCommands ) ):
        submitJob( aDirectoriesAndSbatchCommands[ nNextSubmitCommand ] )
        nNextSubmitCommand += 1


    if ( len( aRunningJobs ) == 0 and nNextSubmitCommand >= len( aDirectoriesAndSbatchCommands ) ):
        break

    waitForAJobToFinish()



printLog( f"finished--not more jobs to submit" )
    
    

        
