### 变迁
要将目标函数改为$\Delta_{p}(x^{'},y)=\sum_{i}\frac{1}{\sqrt{y_{i}+1}}|y_{i}-(A_{p}\cdot x^{'})_{i}|$，我们需要对线性规划问题进行重新建模。具体来说，我们需要将绝对值约束转化为线性约束，并引入辅助变量来表示绝对值。
**目标函数的线性化**
目标函数$\Delta_{p}(x^{'},y)$包含绝对值项，这会导致问题非线性。为了将其转化为线性规划问题，我们可以引入辅助变量$u_i$来表示每个绝对值项:
$$u_i \geq |y_i - (A_p \cdot x^{'})_i|$$
然后，目标函数可以改写为:
$$\Delta_{p}(x^{'},y) = \sum_{i}\frac{1}{\sqrt{y_{i}+1}}u_i$$
为了将$u_i \geq |y_i - (A_p \cdot x^{'})_i|$转化为线性约束，我们可以使用以下两个不等式:
$$u_i \geq y_i - (A_p \cdot x^{'})_i$$
$$u_i \geq (A_p \cdot x^{'})_i - y_i$$

**修改后的线性规划问题可以表示为：**
目标函数：  
$$\quad\min\limits_{i}\frac{1}{\sqrt{y_i+1}}u_i$$  
约束条件：  
$$u_i\geq y_i-(A_p\cdot x'_i)\quad\forall i$$
$$u_i\geq(A_p\cdot x'_i)-y_i\quad\forall i$$  
$$\sum\limits_{i}x'_i\cdot i=N$$  
$$x'_i\geq0\quad\forall i$$  
$$u_i\geq0\quad\forall i$$


### 1. **问题分析**
#### 1.1 约束条件
Unseen 算法的核心约束条件是：
\[
\sum_{i=1}^{n} i \cdot x'_i = N
\]
其中：
- \( x'_i \) 是估计的数据集中恰好出现 \( i \) 次的不同块的数量。
- \( N \) 是数据集的总块数。
#### 1.2 样本比例 \( p \) 的作用
样本比例 \( p \) 是样本大小 \( K_{\text{sample}} \) 与数据集大小 \( N \) 的比值：
\[
p = \frac{K_{\text{sample}}}{N}
\]
因此，理论上 \( N \) 的计算应为：
\[
N = \frac{K_{\text{sample}}}{p}
\]
#### 1.3 为什么 \( N = \frac{K_{\text{sample}}}{p} \) 会导致问题不可行？
当 \( N = \frac{K_{\text{sample}}}{p} \) 时，约束条件 \( \sum_{i=1}^{n} i \cdot x'_i = N \) 可能过于严格，导致以下问题：
1. **样本 DFH 的分布与理论不符**：
   - 如果样本 DFH 的分布与理论期望 \( A_p \cdot x' \) 不符，可能导致约束条件无法满足。
   - 例如，样本中某些频率的块数过多或过少，导致无法通过线性规划找到满足条件的 \( x' \)。
2. **数值不稳定性**：
   - 当 \( p \) 较小（如 \( p = 0.3 \)）时，\( N = \frac{K_{\text{sample}}}{p} \) 会变得非常大。
   - 这可能导致线性规划中的数值计算不稳定，尤其是当 \( A_p \) 矩阵中的某些值非常小或非常大时。
3. **样本 DFH 的稀疏性**：
   - 如果样本 DFH 中有很多零值（即某些频率的块数为零），可能导致约束条件无法满足。
#### 1.4 为什么 \( N = K_{\text{sample}} \times 3.2 \) 可行？
当 \( N = K_{\text{sample}} \times 3.2 \) 时，约束条件 \( \sum_{i=1}^{n} i \cdot x'_i = N \) 变得宽松，使得线性规划更容易找到可行解。这是因为：
- \( N \) 的值变小，约束条件更容易满足。
- 样本 DFH 的分布与理论期望 \( A_p \cdot x' \) 的偏差更容易被容忍。
### 2. **解决方案**
#### 2.1 检查样本 DFH 的合理性
确保样本 DFH 的分布与理论期望一致。可以通过以下方法验证：
- 计算样本的总块数 \( K_{\text{sample}} = \sum_{i=1}^{n} i \cdot y_i \)。
- 检查 \( K_{\text{sample}} \) 是否与 \( p \times N \) 接近。
#### 2.2 调整 \( N \) 的计算方式
 \( N = \frac{K_{\text{sample}}}{p} \) 导致问题不可行，尝试以下方法：
**增加 \( N \) 的容差**：
   - 将约束条件 \( \sum_{i=1}^{n} i \cdot x'_i = N \) 改为 \( \sum_{i=1}^{n} i \cdot x'_i \approx N \)，允许一定的误差范围。
   - 例如，将等式约束改为不等式约束：
     \[
     (1 - \epsilon) N \leq \sum_{i=1}^{n} i \cdot x'_i \leq (1 + \epsilon) N
     \]
     其中 \( \epsilon \) 是一个小的容差（如 0.01）。

**修改后的线性规划问题可以表示为：**
目标函数：  
$$\quad\min\limits_{i}\frac{1}{\sqrt{y_i+1}}u_i$$  
约束条件：  
$$u_i\geq y_i-(A_p\cdot x'_i)\quad\forall i$$
$$u_i\geq(A_p\cdot x'_i)-y_i\quad\forall i$$  
 \[(1 - \epsilon) N \leq \sum_{i=1}^{n} i \cdot x'_i \leq (1 + \epsilon) N \]

$$x'_i\geq0\quad\forall i$$  
$$u_i\geq0\quad\forall i$$