#/bin/bash 

mcl_info=$(ros2 topic echo --once /mcl_pose --csv)
gnss_info=$(ros2 topic echo --once /gnss/fix --csv)

mcl_info=(${mcl_info[0]//,/ })
mcl_x0=${mcl_info[3]}
mcl_y0=${mcl_info[4]}

gnss_info=(${gnss_info[0]//,/ })
gnss_lat0=${gnss_info[5]}
gnss_lon0=${gnss_info[6]}

echo "Get First Point"
read -p "Press Enter to Get Second Point"

mcl_info=$(ros2 topic echo --once /mcl_pose --csv)
gnss_info=$(ros2 topic echo --once /gnss/fix --csv)

mcl_info=(${mcl_info[0]//,/ })
mcl_x1=${mcl_info[3]}
mcl_y1=${mcl_info[4]}

gnss_info=(${gnss_info[0]//,/ })
gnss_lat1=${gnss_info[5]}
gnss_lon1=${gnss_info[6]}

echo "Get Second Point"

cat <<EOF > $1
gauss_kruger_node: 
  ros__parameters:
    p0: [$mcl_x0, $mcl_y0, 0.0]
    gnss0: [$gnss_lat0, $gnss_lon0, 0.0]
    p1: [$mcl_x1, $mcl_y1]
    gnss1: [$gnss_lat1, $gnss_lon1]
    ignore_th_cov: 100.0
EOF

