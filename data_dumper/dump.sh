# eval "$(conda shell.bash hook)"
# conda activate lstm
echo "Pulling from git"
git pull
echo "Running Script"
python3 /home/pi/night-trader/data_dumper/data_dumper.py /home/pi/night-trader/env /home/pi/night-trader/data
echo "Commiting"
git add data/*
DATE=$(date +"%D %H:%M")
echo "Pushing Commit"
git commit -m "New data from [$DATE]"
git push
echo "Done."
