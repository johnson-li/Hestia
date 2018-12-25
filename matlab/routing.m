gcp = [2.2295, 14.020499999999998, 29.4775, 16.5445, 39.4155, 5.4585, 7.644500000000001, 39.763, 3.35, 10.368, 3.5245, 2.5585, 12.4975, 3.536, 2.477, 3.857, 3.2465];
plt = [24.247, 31.3305, 5.4515, 24.3405, 23.143, 16.225, 48.1035, 11.006, 37.203, 11.834, 4.202, 73.102, 46.9315, 46.289, 15.843, 32.123000000000005, 72.264, 8.4725, 5.8115000000000006, 45.6845, 12.8415, 10.443000000000001, 8.9945, 15.8985, 23.938499999999998, 24.972, 10.55, 5.9, 69.307, 8.269, 15.994499999999999, 15.8475, 3.7265, 26.4545, 18.8495, 68.119, 14.475999999999999, 15.724499999999999, 7.737, 12.458, 26.3715, 18.794999999999998, 37.6855, 9.522, 18.144, 3.396, 7.0184999999999995, 14.223500000000001, 17.7885, 13.5245, 56.2315, 20.244999999999997, 18.875, 13.399999999999999, 11.192, 11.1705, 24.644];
aws = [1.115, 1.392, 1.754, 1.2765, 1.1775, 1.145, 2.4465, 1.1805];

hold on
f1 = cdfplot(gcp);
f2 = cdfplot(plt);
f3 = cdfplot(aws);

xlabel('RTT (ms)')
ylabel('CDF')

set(gca,'FontSize',24)
set(f1, 'LineWidth', 1.8, 'LineStyle', '-.', 'Color', [.6 .6 .6]);
set(f2, 'LineWidth', 1.8, 'LineStyle', '--', 'Color', 'black');
set(f3, 'LineWidth', 1.8, 'LineStyle', '-', 'Color', 'r');
legend('Google Cloud', 'PlanetLab', 'AWS', 'Location','southeast')
title('');