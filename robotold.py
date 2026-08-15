#!/usr/bin/env python3
#
# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.


# NO AUTONOMOUS - AFTER TALKING TO ARCHIE

# pylint: disable=pointless-string-statement, attribute-defined-outside-init, missing-function-docstring, missing-module-docstring, missing-class-docstring, too-many-instance-attributes
import wpilib
import wpilib.drive
import rev
from ntcore import NetworkTableInstance



class MyRobot(wpilib.TimedRobot):

    def stop_shooting_motors(self):
        self.left_shooting_motor.set(0)
        self.right_shooting_motor.set(0)

    def start_shooting_motors(self):
        self.left_shooting_motor.set(-self.shooting_speed)
        self.right_shooting_motor.set(self.shooting_speed)

    def rt_pressed(self):
        #print("rt_pressed")
        self.left_shooting_motor.set(-self.shooting_speed)
        self.right_shooting_motor.set(self.shooting_speed)

    def rt_released(self):
        #print("rt_released")
        self.left_shooting_motor.set(0)
        self.right_shooting_motor.set(0)

    def lt_pressed(self):
        #print("lt_pressed")
        self.left_shooting_motor.set(-self.shooting_speed)
        self.right_shooting_motor.set(-self.shooting_speed)

    def lt_released(self):
        #print("lt_released")
        self.left_shooting_motor.set(0)
        self.right_shooting_motor.set(0)


    def rb_pressed(self):
        #print("rb_pressed")
        self.left_motor_group.set(1)
        self.right_motor_group.set(-1)

    def lb_pressed(self):
        #print("lb_pressed")
        self.left_motor_group.set(-1)
        self.right_motor_group.set(1)


    def rb_released(self):
        #print("rb_released")
        self.left_motor_group.set(0)
        self.right_motor_group.set(0)

    def lb_released(self):
        #print("lb_released")
        self.left_motor_group.set(0)
        self.right_motor_group.set(0)


    def robotInit(self):

        self.timer = wpilib.Timer()
        #print("robotInit (robot initialisation function)")

        """Robot initialization function"""

        nt_instance = NetworkTableInstance.getDefault()
        self.smart_dashboard = nt_instance.getTable("SmartDashboard")
        self.power_hub = wpilib.PowerDistribution(7, wpilib.PowerDistribution.ModuleType.kRev)
        self.num_topic = self.smart_dashboard.getDoubleTopic("Battery Voltage")
        self.num_pub = self.num_topic.publish()

        front_left_motor = rev.SparkMax(4, rev.SparkMax.MotorType.kBrushed)
        rear_left_motor = rev.SparkMax(2, rev.SparkMax.MotorType.kBrushed)

        self.left_motor_group = wpilib.MotorControllerGroup(front_left_motor, rear_left_motor)


        front_right_motor = rev.SparkMax(5, rev.SparkMax.MotorType.kBrushed)
        rear_right_motor = rev.SparkMax(1, rev.SparkMax.MotorType.kBrushed)

        self.right_motor_group = wpilib.MotorControllerGroup(front_right_motor, rear_right_motor)

        self.robotDrive = wpilib.drive.DifferentialDrive(
            self.left_motor_group,
            self.right_motor_group
        )
        self.driverController = wpilib.XboxController(0)


        self.right_shooting_motor = rev.SparkMax(3, rev.SparkMax.MotorType.kBrushed)
        self.left_shooting_motor = rev.SparkMax(6, rev.SparkMax.MotorType.kBrushed)

        self.shooting_speed = 1
        self.shootThreshold = 0.5

        # We need to invert one side of the drivetrain so that positive voltages
        # result in both sides moving forward. Depending on how your robot's
        # gearbox is constructed, you might have to invert the left side instead.
        self.right_motor_group.setInverted(True)

        self.loop = wpilib.event.EventLoop()

        self.rt_event = self.driverController.rightTrigger(self.shootThreshold, self.loop)
        self.lt_event = self.driverController.leftTrigger(self.shootThreshold, self.loop)

        self.rb_event = self.driverController.rightBumper(self.loop)
        self.lb_event = self.driverController.leftBumper(self.loop)

        self.rt_event.rising().ifHigh(lambda: self.rt_pressed())
        self.rt_event.falling().ifHigh(lambda: self.rt_released())

        self.lt_event.rising().ifHigh(lambda: self.lt_pressed())
        self.lt_event.falling().ifHigh(lambda: self.lt_released())

        #self.rb_event.rising().ifHigh(lambda: self.rb_pressed())
        #self.rb_event.falling().ifHigh(lambda: self.rb_released())

        #self.lb_event.rising().ifHigh(lambda: self.lb_pressed())
        #self.lb_event.falling().ifHigh(lambda: self.lb_released())



    def robotPeriodic(self):
        self.loop.poll()
        #self.num_pub.set(wpilib.RobotController.getBatteryVoltage())

    def teleopInit(self):
        #print("entering teleopInit (teleoperation/remote control initialisation function)")
        self.robotDrive.arcadeDrive(0, 0)
        self.right_shooting_motor.set(0)
        self.left_shooting_motor.set(0)

    def teleopPeriodic(self):
        # Drive with tank drive.
        # That means that the Y axis of the left stick moves the left side
        # of the robot forward and backward, and the Y axis of the right stick
        # moves the right side of the robot forward and backward.

        left_bumper_down = self.driverController.getLeftBumper()
        right_bumper_down = self.driverController.getRightBumper()
        #loop poll was here before
        if left_bumper_down == right_bumper_down: #no bumpers OR both bumpers: normal tank drive
            self.robotDrive.tankDrive(
                -self.driverController.getLeftY(), -self.driverController.getRightY()
            )
        elif left_bumper_down and not right_bumper_down: # left bumper pressed only
            self.robotDrive.arcadeDrive(0, 1.0, squareInputs=False)
            #self.left_motor_group.set(-1)
            #self.right_motor_group.set(1)
        elif (not left_bumper_down) and right_bumper_down: #right bumper pressed only
            self.robotDrive.arcadeDrive(0, -1.0, squareInputs=False)
            #self.left_motor_group.set(1)
            #self.right_motor_group.set(-1)
        else:
            self.robotDrive.tankDrive(
                -self.driverController.getLeftY(), -self.driverController.getRightY()
            )
            #self.left_motor_group.set(0)
            #self.right_motor_group.set(0)

        #self.loop.poll()

    '''
    if self.driverController.getRightTriggerAxis() > self.shootThreshold:
            pass
        '''


    def autonomousInit(self):
        self.timer.restart()
        #print("Entering autonomousInit (autonomous period initialisation function)")
        #start far right
        #forward under trench
        #turn to balls
        #pick up balls
        #turn
        #shoot

    def autonomousPeriodic(self):
        if self.timer.get() < 0.5:
            self.robotDrive.arcadeDrive(0.7, 0)
            self.right_shooting_motor.set(self.shooting_speed)
            self.left_shooting_motor.set(-self.shooting_speed)
        elif self.timer.get() < 19:
            self.right_shooting_motor.set(self.shooting_speed)
            self.left_shooting_motor.set(-self.shooting_speed)
            self.robotDrive.stopMotor()
        else:
            self.left_shooting_motor.set(0)
            self.right_shooting_motor.set(0)
            self.robotDrive.stopMotor()


        '''
        if self.timer.get() < 19:
            #print("autonomousPeriodic")
            self.left_shooting_motor.set(self.shooting_speed)
            self.right_shooting_motor.set(self.shooting_speed)
            self.robotDrive.arcadeDrive(0, 0)
            self.robotDrive.stopMotor()

        else:
            self.right_shooting_motor.set(0)
            self.left_shooting_motor.set(0)'''






        '''if self.timer.get() < 1.5:
            self.robotDrive.arcadeDrive(0.5, 0, squareInputs=False)

        elif self.timer.get() > 1.5 and self.timer.get() < 2:
            self.robotDrive.arcadeDrive(0, -0.3, squareInputs=False)

        elif self.timer.get() > 2 and self.timer.get() < 3:
            self.robotDrive.arcadeDrive(0.5, 0, squareInputs=False)

        elif self.timer.get() > 3 and self.timer.get() < 3.5:
            self.robotDrive.arcadeDrive(0, -0.3, squareInputs=False)
        
        elif self.timer.get() > 3.5 and self.timer.get() < 4:
            self.robotDrive.arcadeDrive(0, -0.3, squareInputs=False)

        elif self.timer.get() > 4 and self.timer.get() < 5:
            self.robotDrive.arcadeDrive(-1, 0, squareInputs=False)

        elif self.timer.get() > 5 and self.timer.get() < 15:
            self.left_shooting_motor.set(self.shooting_speed)
            self.right_shooting_motor.set(self.shooting_speed)
            self.robotDrive.arcadeDrive(0, 0)

        else:
            self.robotDrive.stopMotor()  # Stop robot
            self.right_shooting_motor.set(0)
            self.left_shooting_motor.set(0)'''
