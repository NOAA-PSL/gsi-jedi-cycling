#!/bin/bash

 python gengsiparmanl.py \
	--textdir=/work2/noaa/da/weihuang/cycling/scripts/gdas-cycling/textdata \
        --type=prepbufr,t,null,t \
        --type=prepbufr,q,null,q \
        --type=prepbufr,uv,null,uv \
        --type=amsuabufr,amsua,n19,amsua_n19 \
        --type=iasibufr,iasi,metop-b,iasi_metop-b

