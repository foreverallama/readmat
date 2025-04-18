classdef NestedClass
    properties
        objProp;
        cellProp;
        structProp;
    end
    methods
        function obj = NestedClass(obj1, obj2, obj3)
            obj.objProp = obj1;
            obj.cellProp{1} = obj2;
            obj.structProp.ObjField = obj3;
        end
    end
end
