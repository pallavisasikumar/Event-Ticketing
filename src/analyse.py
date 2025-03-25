# Python code to plot gas usage (using your data)
import matplotlib.pyplot as plt
blocks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
gas = [0, 483440, 297810, 280638, 280710, 280710, 280662, 280590, 280710, 280650, 280710, 280650]
plt.plot(blocks, gas, marker='o')
plt.xlabel('Block Number')
plt.ylabel('Gas Used')
plt.title('SmartPass Contract Gas Usage During Testing')
plt.show()