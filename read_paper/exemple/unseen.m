function [histx,x] = unseen(f)

% Input: fingerprint f, where f(i) represents number of elements that
% appear i times in a sample. Thus sum_i i*f(i) = sample size.
% File makeFinger.m transforms a sample into the associated fingerprint.

%
% Output: approximation of 'histogram' of true distribution. Specifically,
% histx(i) represents the number of domain elements that occur with
% probability x(i). Thus sum_i x(i)*histx(i) = 1, as distributions have
% total probability mass 1.

%
% An approximation of the entropy of the true distribution can be computed
% as:
%    Entropy = (-1)*sum(histx.*x.*log(x))

f=f(:)';
k=f*(1:size(f,2))'; %total sample size

%%%%%%%% algorithm parameters %%%%%%%%%
gridFactor = 1.1; % the grid of probabilities will be geometric, with...
                % this ratio.
% setting this smaller may slightly increase accuracy, at the cost of speed
alpha = .5; % the allowable discrepancy between the returned solution and...
            % the "best" (overfit).
% 0.5 worked well in all examples we tried, though the results were nearly...
% indistinguishable
% for any alpha between 0.25 and 1. Decreasing alpha increases the...
% chances of overfitting.
xLPMin= 1 / (k*max(10, k));
min_i=min(find(f>0));
if min_i > 1
    xLPMin = min_i / k;
end % minimum allowable probability.
% a more aggressive bound like 1/k^1.5 would make the LP slightly faster,
% though at the cost of accuracy
maxLPiters = 1000; % the 'MaxIter' parameter for Matlabs 'linprog' LP...
                  % solver.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Split the fingerprint into the 'dense' portion for which we
% solve an LP to yield the corresponding histogram, and 'sparse'
% portion for which we simply use the empirical histogram

x = 0;
histx = 0;
fLP = zeros(1, max(size(f)));
for i = 1:max(size(f))
    if f(i) > 0
        wind = [max(1, i - ceil(sqrt(i))), min(i + ceil(sqrt(i)), max(size(f)))];
        if sum(f(wind(1):wind(2))) < sqrt(i) * 2 * sqrt(i)
            x = [x, i / k];
            histx=[histx,f(i)];
            fLP(i)=0;
        else
            fLP(i)=f(i);
        end
    end
end

% If no LP portion, return the empirical histogram
fmax=max(find(fLP>0));
if min(size(fmax))==0
    x=x(2:end);
    histx=histx(2:end);
    return;
end

% Set up the first LP
LPmass=1-x*histx'; % amount of probability mass in the LP region

fLP=[fLP(1:fmax), zeros(1,ceil(sqrt(fmax)))]; 
szLPf=max(size(fiLP)); 
xLPmax=fmax/k; 
xLP=xLPmin*gridFactor.^(0:ceil(log(xLPmax/xLPmin)/log(gridFactor))); 
szLPx=max(size(xLP)); 

objf=zeros(szLPx+2*szLPf,1); 
objf(szLPx+1:2:end)=1./(sqrt(fiLP+1)); % discrepancy in ith fingerprint ...
expectation 
objf(szLPx+2:2:end)=1./(sqrt(fiLP+1)); % weighted by 1/sqrt(f(i)+1)

A = zeros(2*szLPf,szLPx+2*szLPf); 
b=zeros(2*szLPf,1); 
for i=1:szLPf 
    A(2*i-1,1:szLPx)=poisspdf(i,k*xLP); 
    A(2*i,1:szLPx)=(-1)*A(2*i-1,1:szLPx); 
    A(2*i-1,szLPx+2*i-1)=-1; 
    A(2*i,szLPx+2*i)=-1; 
    b(2*i-1)=fiLP(i); 
    b(2*i)=-fiLP(i); 
end 

Aeq = zeros(1,szLPx+2*szLPf); 
Aeq(1:szLPx)=xLP; 
beq = LPMass; 

options = optimset('MaxIter', maxLPiters, 'Display', 'off');
for i = 1:szLPx
    A(:,i) = A(:,i) / xLP(i); % rescaling for better conditioning
    Aeq(i) = Aeq(i) / xLP(i);
end
[sol, fval, exitflag, output] = linprog(objf, A, b, Aeq, beq, ...
    zeros(szLPx+2*szLPf,1), Inf*ones(szLPx+2*szLPf,1), [], options);
if exitflag == 0
    'maximum number of iterations reached--try increasing maxLPiters'
end

if exitflag < 0
    'LP1 solution was not found, still solving LP2 anyway...'
    exitflag
end

% Solve the 2nd LP, which minimizes support size subject to incurring at most
% alpha worse objective function value (of the objective function in the
% previous LP).
objf2=0*objf;
objf2(1:szLPx) = 1; % ensure at most alpha worse obj value
A2=[A; objf']; % than solution of previous LP
b2=[b; fval+alpha];
for i=1:szLPx
    objf2(i)=objf2(i)/xLP(i); % rescaling for better conditioning
end

[sol2, fval2, exitflag2, output] = linprog(objf2, A2, b2, Aeq, beq, ...
    zeros(szLPx+2*szLPf,1), Inf*ones(szLPx+2*szLPf,1), [], options);

if not(exitflag2==1)
    'LP2 solution was not found'
    exitflag2
end

% append LP solution to empirical portion of histogram
sol2(1:szLPx) = sol2(1:szLPx) ./ xLP'; % removing the scaling
x = [x, xLP];
histx = [histx, sol2'];
[x, ind] = sort(x);
histx = histx(ind);
ind = find(histx > 0);
x = x(ind);
histx = histx(ind);


