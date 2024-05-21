# python run_og_usa_ext.py
# python run_og_usa_ext.py --rho_G=0.2
python run_og_usa_ext.py --rho_G=0.3
python run_og_usa_ext.py --rho_G=0.4

for i in `seq i 0.1 0.1 0.4`
do
	for j in `seq j 0.025 0.005 0.35`
	do
		python run_og_usa_ext.py --rho_G=$i --g_y_annual=$j
	done
done