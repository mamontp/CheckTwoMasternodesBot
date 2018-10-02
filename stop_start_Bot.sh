#!/bin/bash

status() {
  if ps -ef |grep CheckTwoMasternodesBot.py |grep -v grep
  then
     echo "CheckTwoMasternodesBot.py start"
  else
     echo "CheckTwoMasternodesBot.py not start"
  fi
}

start() {
  echo "CheckTwoMasternodesBot.py starting"
  if ps -ef |grep CheckTwoMasternodesBot.py |grep -v grep
  then
    echo "CheckTwoMasternodesBot.py already running"
  else
    nohup ./CheckTwoMasternodesBot.py > CheckTwoMasternodesBot.out &
  fi
} 

stop() {
  echo "CheckTwoMasternodesBot.py stoping"
  if ps -ef |grep CheckTwoMasternodesBot.py |grep -v grep
  then
    ps -ef |grep CheckTwoMasternodesBot.py |grep -v grep | awk '{print $2}' | xargs kill
    sleep 5
    ps -ef |grep CheckTwoMasternodesBot.py |grep -v grep | awk '{print $2}' | xargs kill
  else
    echo "Not start CheckTwoMasternodesBot.py"
  fi
}

case "$1" in
    'start')	start;;
    'stop')	stop;;
    'restart')	stop ; echo "Sleeping..."; sleep 1 ;
            	start;;
    'status')	status;;
    *)		echo
            	echo "Usage: $0 { start | stop | restart | status }"
            	echo
            	exit 1
            	;;
esac

exit 0
