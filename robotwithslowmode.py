#!/usr/bin/env python3
#
# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.



# new stuff: stop/start_shooting(), choosing modes, moved polling, A button to move forwards.

# pylint: disable=pointless-string-statement, attribute-defined-outside-init, missing-function-docstring, missing-module-docstring, missing-class-docstring

import wpilib
import wpilib.drive
from wpilib import SendableChooser, SmartDashboard
import rev
from ntcore import NetworkTableInstance



class MyRobot(wpilib.TimedRobot):

    def arcade_drive_wrapper(self, xspeed, zrotation, squareInputs=True):
        self.robotDrive.arcadeDrive(xspeed * self.drive_speed, zrotation, squareInputs=squareInputs)

    def start_blurting_balls(self):
        self.left_shooting_motor.set(self.shooting_speed)
        self.right_shooting_motor.set(self.shooting_speed)

    def stop_shooting_motors(self):
        self.left_shooting_motor.set(0)
        self.right_shooting_motor.set(0)

    def start_shooting(self):
        self.left_shooting_motor.set(-self.shooting_speed)
        self.right_shooting_motor.set(self.shooting_speed)

    def rt_pressed(self):
        self.start_shooting()

    def rt_released(self):
        self.stop_shooting_motors()

    def lt_pressed(self):
        #motors neetd to go bw to suck balls
        self.left_shooting_motor.set(-self.shooting_speed)
        self.right_shooting_motor.set(-self.shooting_speed)

    def lt_released(self):
        self.stop_shooting_motors()


    def rb_pressed(self):
        '''
        self.left_motor_group.set(1)
        self.right_motor_group.set(-1)
        '''
        self.arcade_drive_wrapper(0, 1)
        #self.robotDrive.arcadeDrive(0, 1)
        
    def lb_pressed(self):
        '''
        self.left_motor_group.set(-1)
        self.right_motor_group.set(1)'''
        self.arcade_drive_wrapper(0, -1)
        #self.robotDrive.arcadeDrive(0, -1)


    def rb_released(self):
        '''
        self.left_motor_group.set(0)
        self.right_motor_group.set(0)
        '''
        self.robotDrive.stopMotor()

    def lb_released(self):
        '''
        self.left_motor_group.set(0)
        self.right_motor_group.set(0)
        '''
        self.robotDrive.stopMotor()


    def robotInit(self):

        self.auto_chooser = SendableChooser()
        self.auto_chooser.setDefaultOption("do_nothing", "do_nothing")
        self.auto_chooser.addOption("forward_and_shoot", "forward_and_shoot")
        self.auto_chooser.addOption("oli_auto", "oli_auto")
        self.auto_chooser.addOption("shoot", "shoot")
        self.auto_chooser.addOption("half_sec_back_and_shoot", "half_sec_back_and_shoot")
        
        SmartDashboard.putData("Autonomous Chooser", self.auto_chooser)


        self.timer = wpilib.Timer()
        self.drive_speed = 1

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

        self.robotDrive = wpilib.drive.DifferentialDrive(self.left_motor_group, self.right_motor_group)
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

        self.b_event = self.driverController.B(self.loop)



        self.rt_event.rising().ifHigh(lambda: self.rt_pressed())
        self.rt_event.falling().ifHigh(lambda: self.rt_released())

        self.lt_event.rising().ifHigh(lambda: self.lt_pressed())
        self.lt_event.falling().ifHigh(lambda: self.lt_released())

        self.b_event.rising().ifHigh(lambda: self.start_blurting_balls())
        self.b_event.falling().ifHigh(lambda: self.stop_shooting_motors())
        

        #self.rb_event.rising().ifHigh(lambda: self.rb_pressed())
        #self.rb_event.falling().ifHigh(lambda: self.rb_released())

        #self.lb_event.rising().ifHigh(lambda: self.lb_pressed())
        #self.lb_event.falling().ifHigh(lambda: self.lb_released())



    def robotPeriodic(self):
        self.loop.poll()
        pass
        #self.num_pub.set(wpilib.RobotController.getBatteryVoltage())

    def teleopInit(self):
        self.stop_shooting_motors()
        #self.robotDrive.arcadeDrive(0, 0)
        self.robotDrive.stopMotor()

    def teleopPeriodic(self):
        # Drive with tank drive.
        # That means that the Y axis of the left stick moves the left side
        # of the robot forward and backward, and the Y axis of the right stick
        # moves the right side of the robot forward and backward.

        left_bumper_down = self.driverController.getLeftBumper()
        right_bumper_down = self.driverController.getRightBumper()
        #loop poll was here before
        if self.driverController.getYButton():
            self.arcade_drive_wrapper(1, 0, squareInputs=False)
            #self.robotDrive.arcadeDrive(1, 0, squareInputs=False)
        elif self.driverController.getAButton():
            self.arcade_drive_wrapper(-1, 0, squareInputs=False)


        elif left_bumper_down == right_bumper_down: #no bumpers OR both bumpers: normal tank drive
            self.robotDrive.tankDrive(
                -self.driverController.getLeftY(), -self.driverController.getRightY()
            )
        elif left_bumper_down and not (right_bumper_down): # left bumper pressed only
            self.arcade_drive_wrapper(0, 1, squareInputs=False)
            #self.robotDrive.arcadeDrive(0, 1.0, squareInputs=False)

        elif (not left_bumper_down) and right_bumper_down: #right bumper pressed only
            self.arcade_drive_wrapper(0, -1, squareInputs=False)
            #self.robotDrive.arcadeDrive(0, -1.0, squareInputs=False)

        else: #Something weird
            self.robotDrive.tankDrive(
                -self.driverController.getLeftY(), -self.driverController.getRightY()
            )

        # self.loop.poll()


        if self.driverController.getRightTriggerAxis() > self.shootThreshold:
            pass
            #DO NOT REMOVE FOLLOWING COMMENT:
            #print("shoot the cannon pow pow")

    def autonomousInit(self):
        self.timer.restart()
        self.selected_auto = self.auto_chooser.getSelected()

    def autonomousPeriodic(self):

        if self.selected_auto == "oli_auto":
            print("oli auto")

            if self.timer.get() < 1.5:
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
                self.start_shooting()

            else:
                self.robotDrive.stopMotor()  # Stop robot
                self.stop_shooting_motors()


        elif self.selected_auto == "do_nothing":
            print("do_nothing")
            self.robotDrive.arcadeDrive(0, 0)
            self.stop_shooting_motors()


        elif self.selected_auto == "forward_and_shoot":
            if self.timer.get() > 19:
                print("forward_and_shoot")
                self.robotDrive.arcadeDrive(1, 0, squareInputs=False)
                self.start_shooting()
            else:
                self.robotDrive.stopMotor()
                self.stop_shooting_motors()


        elif self.selected_auto == "shoot":
            if self.timer.get() < 19:
                print("shoot")
                self.start_shooting()
            else:
                self.robotDrive.stopMotor()
                self.stop_shooting_motors()


        elif self.selected_auto == "half_sec_back_and_shoot":
            #ROBOT NEEDS TO BE BACKWARDS

            if self.timer.get() < 0.25:
                self.robotDrive.arcadeDrive(0.7, 0)
                self.start_shooting()
            elif self.timer.get() < 19:
                self.start_shooting()
                self.robotDrive.stopMotor()
            else:
                self.stop_shooting_motors()
                self.robotDrive.stopMotor()
        else:
            print("wrong selection: following else block")
            self.robotDrive.arcadeDrive(0, 0)