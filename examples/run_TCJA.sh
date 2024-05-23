# for frisch in `seq 0.3 0.1 0.5`
# do
# 	for zeta_D in `seq 0.2 0.2 0.6`
# 	do
# 		for g_y_annual in `seq 0.02 0.01 0.04`
# 		do
# 			# for tG1 in `seq 10 10 30`
# 			# do
# 				python run_og_usa_ext.py --frisch=$frisch --zeta_D=$zeta_D --g_y_annual=$g_y_annual
# 			# done
# 		done
# 	done
# done

python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.2 --g_y_annual=0.04
python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.4 --g_y_annual=0.02
python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.4 --g_y_annual=0.03
python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.4 --g_y_annual=0.04
python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.6 --g_y_annual=0.02
python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.6 --g_y_annual=0.03
python run_og_usa_ext.py --frisch=0.3 --zeta_D=0.6 --g_y_annual=0.04

for frisch in `seq 0.4 0.1 0.5`
do
	for zeta_D in `seq 0.2 0.2 0.6`
	do
		for g_y_annual in `seq 0.02 0.01 0.04`
		do
			# for tG1 in `seq 10 10 30`
			# do
				python run_og_usa_ext.py --frisch=$frisch --zeta_D=$zeta_D --g_y_annual=$g_y_annual
			# done
		done
	done
done