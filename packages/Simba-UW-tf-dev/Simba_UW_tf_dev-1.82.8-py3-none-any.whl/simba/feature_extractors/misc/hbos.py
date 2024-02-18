import numpy as np

sample_1 = np.random.randint(0, 1, (100, 6))
sample_2 = np.random.randint(0, 1, (100, 6))

eps        = np.finfo(float).eps
JA,JB    = sample_1.shape[0], sample_2.shape[0]
yA,yB    = np.matrix(sample_1), np.matrix(sample_2)
mA,mB    = yA.mean(axis=0), yB.mean(axis=0)
WA,WB    = np.cov(yA.T), np.cov(yB.T)
W        = ((JA-1)*WA + (JB-1)*WB) / (JA+JB-2) + eps
T2       = (JA*JB)/float(JA+JB)  * (mB-mA) * np.linalg.inv(W) * (mB-mA).T






sample.ndim

# Combine the samples into a single array
data = np.concatenate((sample_1, sample_2))

# Labels for the two groups
groups = np.concatenate((np.zeros(len(sample_1)), np.ones(len(sample_2))))

# Perform Hotelling's T^2 test
result = hotellings(data, groups)

# Extract the Hotelling's T^2 statistic and p-value
t2_statistic = result.statistic
p_value = result.pvalue

print("Calculated t2_statistic:", t2_statistic)
print("P-value:", p_value)
