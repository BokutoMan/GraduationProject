function f = makeFinger(v)
% Input:  vector of integers, v
% Output: vector of fingerprints, f where f(i) = |{j: |{k:v(k)==j}|=i }|
% i.e. f(i) is the number of elements that occur exactly i times in the vector v

h1 = hist(v, min(v):max(v));
f = hist(h1, 0:max(h1));
f = f(2:end);
f = f(:);

% Generate a sample of size 10,000 from the uniform distribution of ...
% support 100,000
n=20; k=10000;
samp = randi(n,k,1);

% Compute corresponding 'fingerprint'
f = makeFinger(samp);

% Estimate distribution from which sample was drawn
[h,x,en]=entropy_est(f);

% output entropy of the true distribution, Unif[n]
trueEntropy = log(n)

% output entropy of the empirical distribution of the sample
empiricalEntropy = -f' * ((1:max(size(f)))/k).*log((1:max(size(f)))/k)' + sum(f)/(2*k)

% output entropy of the recovered histogram, [h,x]
estimatedEntropy = -h*(x.*log(x))

% output support size (# species) of the recovered distribution
suppSz = sum(h)
