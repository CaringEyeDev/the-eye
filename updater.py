import os

cmd_1 = "sudo git --git-dir=/home/pi/the-eye/.git --work-tree=/home/pi/the-eye/ pull"
cmd_2 = "sudo rsync -r /home/pi/the-eye/ /var/www/html/"

returned_value = os.system(cmd_1)
print(returned_value)
returned_value = os.system(cmd_2)
print(returned_value)