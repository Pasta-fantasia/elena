echo '* * * * *'  $HOME/elena/elena.sh >> $HOME/elena/cron.txt
crontab -l | cat - $HOME/elena/cron.txt >crontab.txt && crontab crontab.txt
