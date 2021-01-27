from machine import PWM, Pin
from micropython import const


class Servo:

    def __init__(self, pin_nr):
        self.Pwm = PWM(Pin(pin_nr))
        self.Pwm.freq(50)  # Use 50 Hz as PWM frequency. Most servos work between 1 Hz and 1 kHz.
        self.Duty = 0

    def Start(self):
        self.Pwm.duty(self.Duty)

    def Stop(self):
        self.Pwm.duty(0)

    def SetDuty(self, duty):
        self.Pwm.duty(duty)


class AngularServo(Servo):

    def __init__(self, pin_nr, min_angle, max_angle):
        super().__init__(pin_nr)
        self.MinAngle = min_angle
        self.MaxAngle = max_angle

    def SetAngle(self):
        return


class ContinuousServo(Servo):

    CONTINUOUS_SERVO_DIRECTION_FORWARD = const(0)
    CONTINUOUS_SERVO_DIRECTION_BACKWARD = const(1)

    FORWARD_MIN = const(68)
    FORWARD_MAX = const(1)
    FORWARD_RANGE = const(FORWARD_MAX - FORWARD_MIN)  # -67
    FORWARD_POINT_PER_PERCENT = FORWARD_RANGE / 100  # -0.67

    BACKWARD_MIN = const(69)
    BACKWARD_MAX = const(136)
    BACKWARD_RANGE = const(BACKWARD_MAX - BACKWARD_MIN)  # 67
    BACKWARD_POINT_PER_PERCENT = BACKWARD_RANGE / 100  # 0.67

    def __init__(self, pin_nr):
        super().__init__(pin_nr)
        self.Direction = self.CONTINUOUS_SERVO_DIRECTION_FORWARD

    def SetDirection(self, direction):
        self.Direction = direction

    def SetSpeed(self, percent):
        if self.Direction is self.CONTINUOUS_SERVO_DIRECTION_FORWARD:
            duty = self.FORWARD_MIN + int(self.FORWARD_POINT_PER_PERCENT * percent)
        else:
            duty = self.BACKWARD_MIN + int(self.BACKWARD_POINT_PER_PERCENT * percent)
        self.SetDuty(duty)

