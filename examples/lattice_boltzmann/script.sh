xmgrace -graph 0 -block vz_of_x.0.dat -settype xy -bxy 1:3 -block vz_of_x.100.dat -settype xy -bxy 1:3 -block vz_of_x.200.dat -settype xy -bxy 1:3 -block vz_of_x.300.dat -settype xy -bxy 1:3 -block vz_of_x.400.dat -settype xy -bxy 1:3 -block vz_of_x.500.dat -settype xy -bxy 1:3 -block vz_of_x.600.dat -settype xy -bxy 1:3 -block vz_of_x.700.dat -settype xy -bxy 1:3 -block vz_of_x.800.dat -settype xy -bxy 1:3 -block vz_of_x.900.dat -settype xy -bxy 1:3 -param param_files/plot_2.par -saveall testplot_$1.agr -hardcopy -printfile "testplot_$1.eps" -hdevice EPS
epstopdf testplot_$1.eps
evince testplot_$1.pdf