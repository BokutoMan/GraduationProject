function [histx,x] = unseen(f)

    % 输入：指纹 f，其中 f(i) 表示在样本中出现次数为 i 的元素数量。换句话说，sum_i i*f(i) = 样本大小。
    % 文件 makeFinger.m 将样本转化为相关的指纹。
    
    %
    % 输出：真实分布的“直方图”的近似值。具体来说，
    % histx(i) 表示具有概率 x(i) 的领域元素的数量。因此，sum_i x(i)*histx(i) = 1，
    % 因为分布的总概率质量为 1。
    
    %
    % 真实分布的熵可以通过以下公式进行近似计算：
    %    熵 = (-1)*sum(histx.*x.*log(x))
    
    f=f(:)';  % 将 f 转化为行向量
    k=f*(1:size(f,2))'; % 样本总大小
    
    %%%%%%%% 算法参数 %%%%%%%%%
    gridFactor = 1.1;  % 概率网格将是几何分布，比例为 gridFactor。
                    % 设置这个值较小可能会稍微提高精度，但会降低速度
    alpha = .5;  % 返回的解与“最佳”解（过拟合）之间允许的最大误差。
                % 0.5 在我们尝试的所有示例中效果较好，虽然对于任何 alpha 值在 0.25 和 1 之间，结果几乎无法区分。
                % 减小 alpha 会增加过拟合的几率。
    xLPMin = 1 / (k * max(10, k));  % 最小允许的概率。
    min_i = min(find(f > 0));  % 查找 f 中大于 0 的最小索引
    if min_i > 1
        xLPMin = min_i / k;
    end  % 如果 f 中有大于 0 的元素，更新最小允许的概率。
    % 一个更激进的边界，比如 1/k^1.5，可能会使 LP 稍微更快，但会牺牲精度
    maxLPiters = 1000;  % MATLAB 的 linprog LP 求解器的最大迭代次数。
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % 将指纹分成“密集”部分和“稀疏”部分，对于“密集”部分，我们通过求解线性规划（LP）来得到相应的直方图，
    % 对于“稀疏”部分，我们仅使用经验直方图。
    
    x = 0;
    histx = 0;
    fLP = zeros(1, max(size(f)));
    for i = 1:max(size(f))
        if f(i) > 0
            wind = [max(1, i - ceil(sqrt(i))), min(i + ceil(sqrt(i)), max(size(f)))];
            if sum(f(wind(1):wind(2))) < sqrt(i) % 2 * sqrt(i)
                x = [x, i / k];  % 将概率 x(i) 添加到 x
                histx = [histx, f(i)];  % 将对应的频次添加到 histx
                fLP(i) = 0;
            else
                fLP(i) = f(i);
            end
        end
    end
    
    % 如果没有 LP 部分，返回经验直方图
    fmax = max(find(fLP > 0));
    if min(size(fmax)) == 0
        x = x(2:end);
        histx = histx(2:end);
        return;
    end
    
    % 设置第一个 LP
    LPmass = 1 - x * histx';  % LP 区域中的概率质量
    
    fLP = [fLP(1:fmax), zeros(1, ceil(sqrt(fmax)))]; 
    szLPf = max(size(fLP)); 
    xLPmax = fmax / k; 
    xLP = xLPMin * gridFactor.^(0:ceil(np.log(xLPmax / xLPMin) / np.log(gridFactor))); 
    szLPx = max(size(xLP)); 
    
    objf = zeros(szLPx + 2 * szLPf, 1); 
    objf(szLPx + 1:2:end) = 1 ./ (sqrt(fLP + 1));  % 按照每个 i 的频次计算目标函数
    objf(szLPx + 2:2:end) = 1 ./ (sqrt(fLP + 1));  % 权重为 1/sqrt(f(i)+1)
    
    A = zeros(2 * szLPf, szLPx + 2 * szLPf); 
    b = zeros(2 * szLPf, 1); 
    for i = 1:szLPf 
        A(2 * i - 1, 1:szLPx) = poisspdf(i, k * xLP); 
        A(2 * i, 1:szLPx) = (-1) * A(2 * i - 1, 1:szLPx); 
        A(2 * i - 1, szLPx + 2 * i - 1) = -1; 
        A(2 * i, szLPx + 2 * i) = -1; 
        b(2 * i - 1) = fLP(i); 
        b(2 * i) = -fLP(i); 
    end 
    
    Aeq = zeros(1, szLPx + 2 * szLPf); 
    Aeq(1:szLPx) = xLP; 
    beq = LPmass; 
    
    options = optimset('MaxIter', maxLPiters, 'Display', 'off');
    for i = 1:szLPx
        A(:,i) = A(:,i) / xLP(i);  % 为了更好的条件化，对 A 和 Aeq 进行缩放
        Aeq(i) = Aeq(i) / xLP(i);
    end
    [sol, fval, exitflag, output] = linprog(objf, A, b, Aeq, beq, ...
        zeros(szLPx + 2 * szLPf, 1), np.inf * np.ones(szLPx + 2 * szLPf, 1), [], options);
    
    if exitflag == 0
        disp('最大迭代次数已达到--尝试增加 maxLPiters')
    end
    
    if exitflag < 0
        disp('LP1 解未找到，仍然尝试解 LP2...')
    end
    
    % 求解第二个 LP，最小化支持集的大小，同时确保目标函数的值不超过 alpha 次
    objf2 = 0 * objf;
    objf2(1:szLPx) = 1;  % 确保目标值至多相差 alpha
    A2 = [A; objf'];  % 更新约束矩阵 A
    b2 = [b; fval + alpha];  % 更新约束向量 b
    for i = 1:szLPx
        objf2(i) = objf2(i) / xLP(i);  % 对目标函数进行缩放
    end
    
    [sol2, fval2, exitflag2, output] = linprog(objf2, A2, b2, Aeq, beq, ...
        zeros(szLPx + 2 * szLPf, 1), np.inf * np.ones(szLPx + 2 * szLPf, 1), [], options);
    
    if not(exitflag2 == 1)
        disp('LP2 解未找到')
    end
    
    % 将 LP 解与经验部分的直方图合并
    sol2(1:szLPx) = sol2(1:szLPx) ./ xLP';  % 移除缩放
    x = [x, xLP];
    histx = [histx, sol2'];
    [x, ind] = sort(x);  % 对 x 和 histx 按照 x 排序
    histx = histx(ind);
    ind = find(histx > 0);
    x = x(ind);
    histx = histx(ind);
    