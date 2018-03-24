#!/usr/bin/env bash

if [ -z ${repeat+x} ]
then
    repeat=30
fi
echo repeat: ${repeat}

sudo ping cdn.xuebing.name -c3 -W 4
for i in `seq ${repeat}`
do
    output=`./server/client cdn.xuebing.name`
    cost=`echo "${output}"| grep cost| egrep -o '[0-9.]+'`
    dns_cost=`echo "${output}"| grep 'DNS delay'| egrep -o '[0-9.]+'`
    dns_hit_delay=${dns_hit_delay},${dns_cost}
    if [ -z "$output" ]
    then
        output=0
    fi
    dns_hit_data=${dns_hit_data},${cost}
done
echo dns_hit_data: ${dns_hit_data}
echo dns_hit_delay: ${dns_hit_delay}
