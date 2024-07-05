for frisch in `seq 0.5 -0.1 0.3`
do
	for zeta_D in `seq 0.6 -0.2 0.2`
	do
		for g_y_annual in `seq 0.04 -0.01 0.02`
		do
			# for tG1 in `seq 10 10 30`
			# do
				python run_og_usa_ext.py --frisch=$frisch --zeta_D=$zeta_D --g_y_annual=$g_y_annual
			# done
		done
	done
done