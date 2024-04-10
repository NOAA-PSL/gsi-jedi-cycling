#!/bin/bash

#pick sondes, amsua_n19, iasi_metop-b
 python python_scripts/gengsiparmanl.py \
	--textdir=/work2/noaa/gsienkf/weihuang/gsi/scripts/jedi-cycling/textdata \
        --type=prepbufr,t,null,t \
        --type=prepbufr,q,null,q \
        --type=prepbufr,uv,null,uv \
        --type=amsuabufr,amsua,n19,amsua_n19 \
        --type=iasibufr,iasi,metop-b,iasi_metop-b

 exit 0

#pick sondes only
 python python_scripts/gengsiparmanl.py \
        --textdir=/work2/noaa/gsienkf/weihuang/gsi/scripts/jedi-cycling/textdata \
        --type=prepbufr,t,null,t \
        --type=prepbufr,q,null,q \
        --type=prepbufr,uv,null,uv

