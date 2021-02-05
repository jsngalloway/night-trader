# eval "$(conda shell.bash hook)"
# conda activate lstm
git pull
python3 /home/pi/night-trader/data_dumper/data_dumper.py /home/pi/night-trader/env /home/pi/night-trader/data
git add data/*
DATE=date +"%D %H:%M"
git commit -m "New data from [$DATE]"
git push
