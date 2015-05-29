gprof2dot -f pstats neuroshima.prof | dot -Tdot -o neuroshima.dot
convert neuroshima.dot neuroshima.png
rm *.dot
