import os

cmd = "sudo git --git-dir=/home/pi/the-eye/.git --work-tree=/home/pi/the-eye/ pull"
cmd = "sudo rsync -r /home/pi/the-eye/ /var/www/html/"