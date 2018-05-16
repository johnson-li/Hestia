d = [0.0501750000000003, 0.05907000000000018, 0.07011500000000126, 0.102155, 0.1465399999999999, 0.15479500000000002, 0.17378999999999944, 0.20675999999999917, 0.22602499999999992, 0.22692999999999985, 0.2883450000000001, 0.4710099999999997, 0.49733499999999964, 0.7099100000000007, 0.73559, 0.7688499999999987, 0.7735199999999995, 0.8172329999999999, 0.8609699999999982, 0.9724700000000013, 1.1038049999999995, 1.1435649999999997, 1.324819999999999, 1.54744, 1.581665, 1.58174, 1.596705, 1.7450100000000006, 1.85459, 2.28317, 2.70287, 3.3828249999999986, 3.7163850000000007, 4.406840000000001, 4.604950000000002, 4.614705, 6.219269999999998, 6.263204999999999, 7.334674999999997, 8.428104999999999, 8.866115, 12.19356, 13.383075000000002, 14.293574999999997, 15.420155, 15.815870000000004, 16.84758, 17.71905, 17.86708, 18.147934999999997, 22.560645000000008, 26.045085, 36.61439, 79.86729, 118.98542, 160.573335];

f = cdfplot(d);

xlabel('RTT (ms)')
ylabel('CDF')
title('');
set(gca,'FontSize',16)
set(f, 'LineWidth', 1);
print('figures/anycast-increment','-depsc')

