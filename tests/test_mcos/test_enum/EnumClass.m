classdef EnumClass
   properties
       val;
   end
   enumeration
      enum1 (1)
      enum2 (2)
      enum3 (3)
      enum4 (4)
      enum5 (5)
      enum6 (6)
   end
   methods
       function c = EnumClass(num)
                c.val = num;
        end
    end
end
