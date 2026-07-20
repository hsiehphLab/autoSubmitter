#!/usr/bin/env python


szWorkToDo = "dirsAndSbatchCommands.txt"

import subprocess
import os
from datetime import datetime


nMaximumNumberOfSimultaneousSubmits = 20
nSecondsToSleep = 10

nNextSubmitCommand = 0

aDirectoriesAndSbatchCommands = []
aRunningJobs = []
dictCommandForJobID = {}

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
            szCommand = "sacct -j " + nJob
            # this error handling code was added when there is some cluster problem so that
            # squeue -j returns an error instead of responding with information
            # (DG, Aug 20, 2025)
            try:
                szOutput = subprocess.check_output( szCommand, shell = True ).decode("utf-8")
            except subprocess.CalledProcessError as e:
                printLog(f"CalledProcessError from check_output when running {szCommand}" )
                printLog( str(e.output ) )
                continue

            printLog( f"{szCommand} and got {szOutput}" )
            
            aLines = szOutput.splitlines()

            # looks like:
            #JobID           JobName  Partition    Account  AllocCPUS      State ExitCode 
            #------------ ---------- ---------- ---------- ---------- ---------- -------- 
            #16687086     run_sleep+    agsmall    hsiehph          1    RUNNING      0:0

            assert len( aLines) >= 1, f"{szCommand} returned {szOutput}"


            if ( "RUNNING" not in szOutput and "PENDING" not in szOutput ):
                # get job id
                # might look like (or it could say FAILURE):
                # JobID           JobName  Partition    Account  AllocCPUS      State ExitCode 
                #------------ ---------- ---------- ---------- ---------- ---------- -------- 
                # 7089235      run_bwa_o+      sioux    hsiehph          1  COMPLETED      0:0 
                # 7089235.bat+      batch               hsiehph          1  COMPLETED      0:0 
                # 7089235.ext+     extern               hsiehph          1  COMPLETED      0:0 
                # 0              1              2
                if ( "COMPLETED" in szOutput ):
                    szStatus = "finished"
                elif( "FAILED" in szOutput ):
                    szStatus = "failed"
                else:
                    szStatus = "uncertain"

                if ( len( aLines ) < 2 ):
                    # not sure how this could happen but it does.  I
                    # think it might be that the node is not in touch
                    # with the scheduler so gives this response:
                    # slurm_load_jobs error: Unable to contact slurm
                    # controller (connect failure)
                    # What to do?  job might be running.  job might have failed.
                    # job might have completed.  So just leave it in the RUNNING
                    # queue to check on it again in a little while.
                    printLog( f"{szCommand} returned {szOutput} so will assume it is RUNNING" )
                    continue
                    
                szImportantLine = aLines[ 2 ]

                aWords = szImportantLine.split()

                if ( len( aWords ) < 1 ):
                    printLog( f"{szCommand} returned {szOutput} with only" + str( len( aWords ) ) + f" on line {szImportantLine}" )
                    # I'm not aware of this ever happening, but just in case,
                    # I'm handling it
                    continue

                szCommandSubmitted = dictCommandForJobID[nJob]

                printLog( f"{szCommandSubmitted} {szStatus} with {szOutput} jobid {nJob}")
                del dictCommandForJobID[ nJob ]
                aRunningJobs.remove( nJob )
                bJobFinished = True
                # do not continue to look at other jobs but submit a new job immediately
                break

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
    dictCommandForJobID[ szJobID ] = szDirectoryAndSbatchCommand
    
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



printLog( f"autoSubmitter.py ending--no more jobs to submit" )
    
    

        
