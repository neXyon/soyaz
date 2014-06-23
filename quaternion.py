import math

class Quaternion :
    w = 1
    x = 0
    y = 0
    z = 0
    
    def __init__(self, q = (1, 0, 0, 0)) :
        self.w = q[0]
        self.x = q[1]
        self.y = q[2]
        self.z = q[3]
    
    def getLookAt(self) :
        return (-2 * (self.w * self.y + self.x * self.z),
                2 * (self.x * self.w - self.z * self.y),
                2 * (self.x * self.x + self.y * self.y) - 1)
    
    def getUp(self) :
        return (2 * (self.x * self.y - self.w * self.z),
                1 - 2 * (self.x * self.x + self.z * self.z),
                2 * (self.w * self.x + self.y * self.z))

    def __add__(self, other) :
        return Quaternion((self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z))
    
    def __mul__(self, other) :
        return Quaternion(( self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
                            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
                            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
                            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w ))

    def dot(self, other) :
        return self.w * other.w + self.x * other.x + self.y * other.y + self.z * other.z
    
    def norm(self) :
        return self.dot(self)
    
    def length(self) :
        return math.sqrt(self.norm())
    
    def normalize(self) :
        l = self.length()
        self.w /= l
        self.x /= l
        self.y /= l
        self.z /= l
        return self
    
    def conjugate(self) :
        self.x = -self.x
        self.y = -self.y
        self.z = -self.z
        return self
    
    def rotate(self, axis, angle) :
        s = math.sin(angle * .5)
        r = Quaternion((math.cos(angle * .5), axis.x * s, axis.y * s, axis.z * s))
        return self * r

    def toEuler(self) :
        test = self.x * self.y + self.z * self.w
        if test > 0.4999999 :
            return ( 2 * math.atan2(self.x, self.w),  math.pi / 2, 0)
        elif test < -0.499999:
            return (-2 * math.atan2(self.x, self.w), -math.pi / 2, 0)
        
        sqw = self.w * self.w
        sqx = self.x * self.x
        sqy = self.y * self.y
        sqz = self.z * self.z

        return (math.atan2(2 * (self.w * self.x + self.y * self.z), 1 - 2 * (sqx + sqy)),
                math.asin(-2 * (self.x * self.z - self.w * self.y)),
                math.atan2(2 * (self.x * self.y + self.w * self.z), 1 - 2 * (sqy + sqz)))

        #return (math.atan2(2 * (self.w * self.z + self.x * self.y), 2 * (sqy + sqz) - 1),
        #        math.asin(-2 * (self.w * self.y - self.x * self.z)),
        #        math.atan2(2 * (self.w * self.x + self.y * self.z), 2 * (sqw + sqz) - 1))

        #return (math.atan2(2 * (self.y * self.z + self.w * self.x), sqw - sqx - sqy + sqz),
        #         math.asin(-2 * (self.x * self.z - self.w * self.y)),
        #         math.atan2(2 * (self.x * self.y + self.w * self.z), sqw + sqx - sqy - sqz))

        #return (math.atan2(2 * (self.y * self.w - self.x * self.z), 1 - 2 * (sqy + sqz)),
        #         math.asin(2 * self.x * self.y + self.z * self.w),
        #         math.atan2(2 * (self.x * self.w - self.y * self.z), 1 - 2 * (sqx + sqz)))
