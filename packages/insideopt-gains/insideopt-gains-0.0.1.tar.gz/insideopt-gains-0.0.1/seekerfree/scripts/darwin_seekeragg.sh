echo $$ > $1/seekeragg.pid

for (( c=0; c< $4 ; c++ )) do
  sleep 2
  outFiles=$(gfind $1 -name out\*.file -printf '%P,')
  ${SeekerPath}/bin/coll $1 $2 $3 ${outFiles}
done


