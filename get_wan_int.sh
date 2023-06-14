echo $(ip route get 8.8.8.8 | awk -- '{printf $5}')
