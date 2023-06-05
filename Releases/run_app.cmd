@echo off
start cmd /k bin\run_mes.cmd
timeout 6
start cmd /k bin\run_erp.cmd
start cmd /k java -jar bin\plant\sfs.jar

