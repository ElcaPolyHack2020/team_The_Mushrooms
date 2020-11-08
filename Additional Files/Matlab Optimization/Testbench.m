clear
clc
grandCycles=1000;
Bussize=8;
Data1(grandCycles,1)=0;
Data2(grandCycles,1)=0;
Data3(grandCycles,1)=0;
Data4(grandCycles,1)=0;

MyDistribution= [1, 0; 0.6, 0.4; 0.55, 0.45; 0.52, 0.48; 0.5, 0.5; 0.48, 0.52; 0.45, 0.55;0.4, 0.6; 0, 1];
MyDistribution3= [1, 0; 7/8, 1/8; 6/8, 2/8; 5/8, 3/8; 4/8, 4/8; 3/8, 5/8; 2/8, 6/8;1/8, 7/8; 0, 1];
MyDistribution4= [1, 0; 0.6, 0.4; 0.55, 0.45; 0.5, 0.5; 0.45, 0.55; 0.4, 0.6; 0.35, 0.65;0.3, 0.7; 0, 1];

%8 place bus
for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    %closest drop off closer that closest pickup AND not empty
    %OR bus full
    
    if((min1 > min2) && (sum(Bus(:,1)) ~= 0))||(sum(Bus(:,1)) == Bussize)
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif (min1 <= min2) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data1(iterator, 1) = Distance;
end

for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    % Weighted closest drop off closer that closest pickup AND not empty
    %OR bus full
    if      (MyDistribution(sum(Bus(:,1))+1 ,2)* min1) > (MyDistribution(sum(Bus(:,1))+1 ,1)* min2 ) %&& (sum(Bus(:,1)) ~= 0)) || (sum(Bus(:,1)) == 8) 
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif ( (MyDistribution(sum(Bus(:,1))+1 ,2)) *min1 < (MyDistribution(sum(Bus(:,1))+1 ,1)) * min2 ) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data2(iterator, 1) = Distance;
end

for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    % Weighted closest drop off closer that closest pickup AND not empty
    %OR bus full
    if      (MyDistribution3(sum(Bus(:,1))+1 ,2)* min1) > (MyDistribution3(sum(Bus(:,1))+1 ,1)* min2 ) %&& (sum(Bus(:,1)) ~= 0)) || (sum(Bus(:,1)) == 8) 
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif ( (MyDistribution3(sum(Bus(:,1))+1 ,2)) *min1 < (MyDistribution3(sum(Bus(:,1))+1 ,1)) * min2 ) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data3(iterator, 1) = Distance;
end

for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    % Weighted closest drop off closer that closest pickup AND not empty
    %OR bus full
    if      (MyDistribution4(sum(Bus(:,1))+1 ,2)* min1) > (MyDistribution4(sum(Bus(:,1))+1 ,1)* min2 ) %&& (sum(Bus(:,1)) ~= 0)) || (sum(Bus(:,1)) == 8) 
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif ( (MyDistribution4(sum(Bus(:,1))+1 ,2)) *min1 < (MyDistribution4(sum(Bus(:,1))+1 ,1)) * min2 ) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data4(iterator, 1) = Distance;
end

x= linspace(1,grandCycles, grandCycles);
Data1= sort(transpose(Data1));
Data2= sort(transpose(Data2));
Data3= sort(transpose(Data3));
Data4= sort(transpose(Data4));

figure
plot (x,Data1,x,Data2,'g',x,Data3,'r',x,Data4,'c')
title('Optimisation Evaluation 8 place Bus - Capacity utilisation')
xlabel('x - Iterations')
ylabel('Distance')


Bussize=4;
Bus(5:8,:) = [];
MyDistribution= [1, 0; 0.55, 0.45; 0.5, 0.5;  0.45, 0.55; 0, 1];
MyDistribution3= [1, 0;  6/8, 2/8;  4/8, 4/8; 2/8, 6/8; 0, 1];
MyDistribution4= [1, 0;  0.55, 0.45; 0.45, 0.55; 0.35, 0.65; 0, 1];
Data5=0;
Data6=0;
Data7=0;
Data8=0;
%4 place bus
for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    %closest drop off closer that closest pickup AND not empty
    %OR bus full
    
    if((min1 > min2) && (sum(Bus(:,1)) ~= 0))||(sum(Bus(:,1)) == Bussize)
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif (min1 <= min2) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data5(iterator, 1) = Distance;
end

for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    % Weighted closest drop off closer that closest pickup AND not empty
    %OR bus full
    if      (MyDistribution(sum(Bus(:,1))+1 ,2)* min1) > (MyDistribution(sum(Bus(:,1))+1 ,1)* min2 ) %&& (sum(Bus(:,1)) ~= 0)) || (sum(Bus(:,1)) == 8) 
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif ( (MyDistribution(sum(Bus(:,1))+1 ,2)) *min1 < (MyDistribution(sum(Bus(:,1))+1 ,1)) * min2 ) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data6(iterator, 1) = Distance;
end

for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    % Weighted closest drop off closer that closest pickup AND not empty
    %OR bus full
    if      (MyDistribution3(sum(Bus(:,1))+1 ,2)* min1) > (MyDistribution3(sum(Bus(:,1))+1 ,1)* min2 ) %&& (sum(Bus(:,1)) ~= 0)) || (sum(Bus(:,1)) == 8) 
        b = min2_coordinate;
        
        Distance = Distance + min2; %sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif ( (MyDistribution3(sum(Bus(:,1))+1 ,2)) *min1 < (MyDistribution3(sum(Bus(:,1))+1 ,1)) * min2 ) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1; %sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data7(iterator, 1) = Distance;
end

for (iterator=1:grandCycles)
Bus(Bussize,3) = 0;
Bus_coo = rand(1,2);
Distance = 0;
Pedestrians = rand(1,2);
counter = 0;
unloaded=0;
for a = 1:1000
    if(rand(1) > 0.5)   
        counter = counter + 1;
        Pedestrians(size(transpose(Pedestrians),2)+1,2) = rand(1);
        Pedestrians(size(transpose(Pedestrians),2),1) = rand(1);
    end
    
    %closest Pedest
    min1 = 2;
    min1_coordinate = 0;
    for b=1:size(transpose(Pedestrians),2)
        
        if min1 > sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2)
            min1 = sqrt((Pedestrians(b,1)-Bus_coo(1,1))^2 + (Pedestrians(b,2)-Bus_coo(1,2))^2);
            min1_coordinate = b;
        end
    end
    
    %closest unload
    min2 = 2;
    min2_coordinate = 0;
    for b=1:Bussize
        if Bus(b,1) == 1
            
            if min2 > sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2)
                min2 = sqrt((Bus(b,2)-Bus_coo(1,1))^2 + (Bus(b,3)-Bus_coo(1,2))^2);
                min2_coordinate = b;
            end
        end
    end
    
    %unload
    % Weighted closest drop off closer that closest pickup AND not empty
    %OR bus full
    if      (MyDistribution4(sum(Bus(:,1))+1 ,2)* min1) > (MyDistribution4(sum(Bus(:,1))+1 ,1)* min2 ) %&& (sum(Bus(:,1)) ~= 0)) || (sum(Bus(:,1)) == 8) 
        b = min2_coordinate;
        
        Distance = Distance + min2; 
        Bus_coo = [Bus(b,2),  Bus(b,3)];
        Bus (b,1:3) = 0;
        unloaded=unloaded+1; 
       
    %pick up
    elseif ( (MyDistribution4(sum(Bus(:,1))+1 ,2)) *min1 < (MyDistribution4(sum(Bus(:,1))+1 ,1)) * min2 ) && ~(isempty(Pedestrians))
        b = min1_coordinate;
        
        Distance = Distance + min1;
        Bus_coo =[Pedestrians(b,1),  Pedestrians(b,2)];
        
        d = 1;
        c = 0;
        while(d && c < Bussize)
            c = c + 1;
            if Bus(c,1) == 0
                Bus(c,1) = 1;
                Bus(c,2) = rand(1);
                Bus(c,3) = rand(1);
                d =0;
            end
        end
        Pedestrians(b,:) = [];
    end
    

Distance;
counter;
end

Data8(iterator, 1) = Distance;
end


x= linspace(1,grandCycles, grandCycles);
Data5= sort(transpose(Data5));
Data6= sort(transpose(Data6));
Data7= sort(transpose(Data7));
Data8= sort(transpose(Data8));

figure
plot (x,Data5,x,Data6,'g',x,Data7,'r',x,Data8,'c')
title('Optimisation Evaluation 4 place Bus - Capacity utilisation')
xlabel('x - Iterations')
ylabel('Distance')

