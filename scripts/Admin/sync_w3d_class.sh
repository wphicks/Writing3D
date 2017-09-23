#!/bin/bash
RCLONE="/home/cavedemo/W3DClassSync/rclone_bin/rclone --delete-after"

LOCAL_PRE="/share/cavewriting/classes/w3d2017fall"

drive_names=("Blake" "Charles" "Dani" "Griffin" "Jack" "Liesl" "Lucas" "Meredith" "Michael" "Olivia" "Sally" "Scott" "Theadora" "Tim" "Zhean")

#local_names=("hequet" "perez" "solayappan" "shin" "douglas" "han" "francois" "tachihara" "giannazzo" "bayer" "burke" "swanson" "vann" "dingsun" "ziebell")

for i in "${!drive_names[@]}"; do
    $RCLONE sync "W3D:w3d2017Fall_Shared/${drive_names[$i]}/kioskButton" "$LOCAL_PRE/${drive_names[$i]}"
done

$RCLONE copy W3D:w3d2017Fall_Shared/Fonts /share/cavewriting/CW2/fonts
